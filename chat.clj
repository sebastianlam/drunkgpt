(ns chat
  (:require [clj-http.client :as http]
            [clojure.data.json :as json]
            [clojure.java.io :as io]
            [tts-say.core :as tts]))

(def LOG_FILE "log.json")
(def PERSONAS_FILE "personas.json")
(def ^:dynamic OPENAI_API_KEY (System/getenv "OPENAI_API_KEY"))

; Load personas
(def personas
  (with-open [reader (io/reader PERSONAS_FILE)]
    (json/read reader)))

(def persona-options (keys personas))
(def persona-display (zipmap (range 1 (inc (count persona-options))) persona-options))

; Speaker configuration
(def engine (tts/init-speech-handler))

; Functions
(defn time-str []
  (str (java.time.LocalDateTime/now)))

(defn startup-check []
  (if (and (io/file LOG_FILE) (.canRead (io/as-file LOG_FILE)))
    (println "Log loaded.")
    (do (println "Either file is missing or is not readable, creating file...")
        (.write (io/writer (io/file LOG_FILE)) (json/write-str {"chats" []})))))

(defn json-log [f-name key data]
  (let [old-data (-> (slurp f-name)
                     (json/read-str :key-fn keyword))]
    (-> (update old-data key conj data)
        (json/write-str :pretty true)
        (spit f-name))))

(defn session-log! [context init-time model is-end?]
  (let [log-content {"start" init-time
                     "end" (time-str)
                     "model" model
                     "content" context}]
    (json-log LOG_FILE :chats log-content)
    (when is-end? (println "\nAuf Wiedersehen!") (System/exit 0))))

(defn talk! [string]
  (tts/speech-handler string))

(defn model-prompt [model-display]
  (let [display (apply str (map (fn [[k v]] (str "(" k ") " v "\n")) model-display))]
    (loop []
      (print (str "Choose your model:\n" display))
      (flush)
      (let [choice (try
                     (Integer/parseInt (read-line))
                     (catch Exception e nil))]
        (if-let [model (model-display choice)]
          (do (println (str "You have chosen " model)) model)
          (recur))))))

(defn persona-input [options is-continue context time model]
  (let [display (apply str (map (fn [[k v]] (str "(" k ") " v "\n")) options))]
    (loop []
      (print (str "Choose your fighter:\n" display))
      (flush)
      (let [choice (try
                     (Integer/parseInt (read-line))
                     (catch Exception e nil))]
        (if-let [choice-option (options choice)]
          (do (when is-continue
                (session-log! context time model false))
              (println (str "You have chosen " choice-option))
              (let [new-context (conj context {"role" "system" "content" (personas choice-option)})]
                [choice-option new-context]))
          (recur))))))

(defn main
  [& args]
  (let [_ (startup-check)
        start-time (time-str)
        _ (println "Initialising...")
        model-id (model-prompt model-display)
        [agent context-arr] (persona-input persona-display false [] start-time model-id)]
    (println "(input \"new\" for session change)") 
    (doseq [prompt-idx (iterate inc 1)]
      (defn handle-input [context-arr start-time model-id]
        (let [prompt-io (read-line)]
          (cond
            (empty? prompt-io)
            (do (println "Give me something mate.") (handle-input context-arr start-time model-id))

            (.equalsIgnoreCase "new" prompt-io)
            (do (let [[new-agent new-context-arr] (persona-input persona-display true context-arr start-time model-id)]
                  (reset! agent new-agent)
                  (reset! context-arr new-context-arr)
                  (reset! start-time (time-str))
                  (handle-input context-arr start-time model-id)))

            :else
            (do (reset! context-arr (conj context-arr {"role" "user" "content" prompt-io}))
                (let [response (-> (http/post (str "https://api.openai.com/v1/engines/" model-id "/completions")
                                               {:headers {:authorization (str "Bearer " (str OPENAI_API_KEY))}
                                   :content-type "application/json"
                                   :body (json/write-str {"messages" context-arr})})
                                 (json/read-str :key-fn keyword))
                      assist (-> response :choices first :message)
                      cost (-> response :usage)]
                  (println (str "\n" agent ":\n" (:content assist) "\n" cost '\n""))
                  (talk! (:content assist))
                  (reset! context-arr (conj context-arr assist))
                  (handle-input context-arr start-time model-id)))))))
    (handle-input context-arr start-time model-id)))

(main)