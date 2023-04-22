(ns chat
  (:require [clojure.java.io :as io]
            [clj-http.client :as client]
            [cheshire.core :as json]
            [java-time :as jt]))

(defn time-str []
  (jt/toString (jt/instant)))

(defn startup-check! [log-file]
  (when-not (.exists (io/file log-file))
    (with-open [db-file (io/writer (io/file log-file))]
      (.write db-file (json/generate-string {:chats []})))
    (prn "Log created.")))

(defn json-log! [f-name key data]
  (let [old-data (-> f-name slurp json/parse-string)]
    (with-open [json-file (io/writer f-name)]
      (.write json-file
        (json/generate-string (update old-data key conj data) :pretty true)))))

(defn request-response [api-key model messages]
  (-> (client/post
        "https://api.openai.com/v1/engines/davinci-codex/completions"
        {:body (json/generate-string {:model model, :messages messages})
         :headers {"Authorization" (str "Bearer " api-key), "Content-Type" "application/json"}
         :content-type :json, :accept :json})
      :body json/parse-string :choices first :message))

(defn input [prompt]
  (print prompt)
  (flush) ;; Flush helps ensure the prompt appears properly before waiting for the user.
  (read-line))

(defn prompt-session [log-file person persona]
  (let [init-time (time-str)
        model "text-davinci-002"
        openid (System/getenv "OPENAI_API_KEY")
        context [{:role "system", :content (get persona person)}]
        msg-loop (fn process-msgs [context]
                   (let [content (input "\nUser:\n")
                         context (conj context {:role "user", :content content})
                         answer (->> context (request-response openid model) :content)
                         cost-display (str (->> context (request-response openid model) :usage))]
                     (println (str "\n" person ": " answer "\n" cost-display "\n"))
                     (json-log! log-file "chats" {:start init-time, :end (time-str), :model model, :content context})
                     (recur (conj context {:role "assistant", :content answer}))))]
    (startup-check! log-file)
    (msg-loop context)))

(defn select-persona [personas]
  (prn "Choose your fighter:")
  (doseq [[idx persona] (map-indexed vector personas)]
    (prn (str "(" (inc idx) ") " persona)))
  (let [choice (dec (Integer/parseInt (input "")))]
    (if (< choice (count personas))
      (nth personas choice)
      (do (prn "Invalid choice") (select-persona personas)))))

(defn main []
  (let [personas-json (-> "personas.json" slurp json/parse-string)
        person (select-persona (keys personas-json))]
    (prompt-session "log.json" person personas-json)
    (flush)))

(main)