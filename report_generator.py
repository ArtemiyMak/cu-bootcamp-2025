import time
import requests
from openai import OpenAI
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID

def report_gen(params, answers, language):
    """Генерация отчета с использованием YandexGPT."""
    print(f"--- REPORT_GEN (YANDEX) DEBUG ---")
    print(f"Params: {params}")
    print(f"Answers: {answers}")
    print(f"Language: {language}")
    
    folder_id = YANDEX_FOLDER_ID
    api_key = YANDEX_API_KEY
    gpt_model = 'yandexgpt-lite'

    system_prompt = (
        "Придумай цельный отчет. Без дополнительного оформления, цельным текстом. Далее будут даны параметры и ответы на них, "
        "напиши связный цельный текст, описывающий прошедший урок, будь креативным, развернуто используй данные параметры и ответы "
        "для создания человекоподобного текста." if language == "ru" else
        "Create a comprehensive report. Without additional formatting, as a continuous text. Below will be given parameters and answers to them, "
        "write a coherent and comprehensive text describing the past lesson in detail. Be creative and use the provided parameters and answers extensively. "
        "Include specific examples, elaborate on key points, and provide a thorough analysis of the lesson. Ensure the text is engaging, informative, and human-like, "
        "with a natural flow and a length that is approximately 1.5 to 2 times longer than usual. USE ONLY ENGLISH LANGUAGE STRICTLY" if language == "en" else
        "Crea un rapporto completo. Senza formattazione aggiuntiva, come testo continuo. Di seguito verranno forniti parametri e risposte, "
        "scrivi un testo coerente e completo che descriva la lezione passata in dettaglio. Sii creativo e utilizza i parametri e le risposte fornite in modo esteso. "
        "Includi esempi specifici, approfondisci i punti chiave e fornisci un'analisi approfondita della lezione. Assicurati che il testo sia coinvolgente, informativo e simile a quello umano, "
        "con un flusso naturale e una lunghezza approssimativamente 1,5-2 volte maggiore del solito. UTILIZZARE ESCLUSIVAMENTE LA LINGUA ITALIANA " if language == "it" else
        "Erstelle einen umfassenden Bericht. Ohne zusätzliche Formatierung, als fortlaufender Text. Es werden Parameter und Antworten darauf gegeben, "
        "schreibe einen zusammenhängenden und umfassenden Text, der die vergangene Stunde detailliert beschreibt. Sei kreativ und verwende die bereitgestellten Parameter und Antworten ausführlich. "
        "Füge spezifische Beispiele hinzu, gehe auf Schlüsselpunkte ein und liefere eine gründliche Analyse der Stunde. Achte darauf, dass der Text ansprechend, informativ und menschenähnlich ist, "
        "mit einem natürlichen Fluss und einer Länge, die etwa 1,5- bis 2-mal länger ist als üblich. VERWENDEN SIE AUSSCHLIESSLICH DIE DEUTSCHE SPRACHE"
    )

    user_prompt = (
        "Параметры для отчета:\n" + "\n".join(params) + "\n\nОтветы:\n" + "\n".join(answers) if language == "ru" else
        "Parameters for the report:\n" + "\n".join(params) + "\n\nAnswers:\n" + "\n".join(answers) if language == "en" else
        "Parametri per il rapporto:\n" + "\n".join(params) + "\n\nRisposte:\n" + "\n".join(answers) if language == "it" else
        "Parameter für den Bericht:\n" + "\n".join(params) + "\n\nAntworten:\n" + "\n".join(answers)
    )

    print(f"System prompt: {system_prompt[:100]}...")
    print(f"User prompt: {user_prompt[:100]}...")

    try:
        body = {
            'modelUri': f'gpt://{folder_id}/{gpt_model}',
            'completionOptions': {'stream': False, 'temperature': 1, 'maxTokens': 5000},
            'messages': [
                {'role': 'system', 'text': system_prompt},
                {'role': 'user', 'text': user_prompt},
            ],
        }
        url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Api-Key {api_key}'
        }
        print("Making request to Yandex API...")
        response = requests.post(url, headers=headers, json=body)
        operation_id = response.json().get('id')
        print(f"Got operation ID: {operation_id}")
        
        url = f"https://llm.api.cloud.yandex.net:443/operations/{operation_id}"
        headers = {"Authorization": f"Api-Key {api_key}"}
        print("Waiting for completion...")
        while True:
            response = requests.get(url, headers=headers)
            done = response.json()["done"]
            if done:
                print("Request completed")
                break
            time.sleep(2)
        data = response.json()
        answer = data['response']['alternatives'][0]['message']['text']
        print(f"Answer received: {answer[:100]}...")
        return answer
    except Exception as e:
        print(f"Error in report_gen (Yandex): {e}")
        return f"Не удалось сгенерировать отчет через Yandex API. Ошибка: {str(e)[:100]}"


def report_gen_gpt(params, answers, language):
    """Генерация отчета с использованием Mistral API."""
    print(f"--- REPORT_GEN_GPT DEBUG ---")
    print(f"Params: {params}")
    print(f"Answers: {answers}")
    print(f"Language: {language}")
    
    base_url = "https://api.aimlapi.com/v1"
    api_key = "028b03024e454ea1a156d289a7003dce"  # Замените на ваш API ключ
    
    system_prompt = (
        "детальный отчет по русски параметры:дата урока,время начала/конца,имя/возраст студента,тема,ДЗ,отзыв ученика,комм. репет." if language == "ru" else
        "detailed report in English.Use:Lesson date,start/end time,student name/age,topic,homework,feedback,tutor comment" if language == "en" else
        "un rapporto dettagliato in italiano.Usa:data lezione,ora inizio/fine,nome/età studente,argomento,compiti,feedback,commento tutor" if language == "it" else
        "Erstelle detaillierten Bericht auf Deutsch.Nutze:Datum, Start / Ende, Name / Alter, Thema, Hausaufgaben, Feedback, Kommentar."
    )

    user_prompt = (
        "\n\nОтветы:\n" + "\n".join(answers) if language == "ru" else
        "\n\nAnswers:\n" + "\n".join(answers) if language == "en" else
        "\n\nRisposte:\n" + "\n".join(answers) if language == "it" else
        "\n\nAntworten:\n" + "\n".join(answers)
    )
    
    print(f"System prompt: {system_prompt}")
    print(f"User prompt: {user_prompt}")
    
    try:
        api = OpenAI(api_key=api_key, base_url=base_url)
        print("OpenAI client created successfully")
        
        completion = api.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=256,
        )
        print("API request completed successfully")
        
        response = completion.choices[0].message.content
        print(f"Response received: {response[:100]}...")  # Вывод первых 100 символов
        return response
    except Exception as e:
        print(f"Error in report_gen_gpt: {e}")
        # Возвращаем заглушку в случае ошибки
        return f"Не удалось сгенерировать отчет. Ошибка: {str(e)[:100]}" 