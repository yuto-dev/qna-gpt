import logging
import requests
import asyncio
from datetime import datetime as rolex
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

tokenKey = "REPLACE"
queueURL = "http://localhost:8000"
dbURL = "http://localhost:8003"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot and I'm online, please talk to me!")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = "Halo, saya KayuMerantiBot. Untuk memulai, silahkan ketik /prompt lalu lanjutkan dengan pertanyaan yang ada ingin anda tanyakan. \n" + "\nContoh: /prompt Apakah yang membuat langit berwarna biru?"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='Markdown')

async def prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    prompt = ' '.join(context.args)
    
    data = {
        "prompt": prompt,
        "chatID": update.effective_chat.id
    }

    dbInsertUrl = dbURL + "/insert_chat"
    response = requests.post(dbInsertUrl, json=data)

    if response.status_code == 200:
        startTime = rolex.now()
        notificationMessage = "*Processing prompt:* \n" + prompt + "\n\n" + "*Time start: " + startTime.strftime("%Y-%m-%d %H:%M:%S") + " (GMT +7)*"
        # Process the argument as needed
        # For demonstration, just echo back the argument
        await context.bot.send_message(chat_id=update.effective_chat.id, text=notificationMessage, parse_mode='Markdown')
        
        print("Data inserted successfully")
        startTime = rolex.now()
        insertData = response.json()
        responseId = insertData.get("id")
        print("Processing entry ID: ", responseId)
        
        while True:
            
            url = dbURL + "/get_flagA"
            headers = {"Content-Type": "application/json"}
            data = {"id": responseId}

            response = requests.get(url, headers=headers, json=data)
            response_data = response.json()
            flagA = response_data.get("flagA")
            
            if flagA == 1:
                break  
            
            
        
        url = dbURL + "/get_result"
        headers = {"Content-Type": "application/json"}
        data = {"id": responseId}
        response = requests.get(url, headers=headers, json=data)
        response_data = response.json()
        
        response = response_data.get("response")
        sourceA = response_data.get("sourceA")
        sourceB = response_data.get("sourceB")
        
        sourceList = []
        sourceList.append(sourceA)
        sourceList.append(sourceB)
        
        updateData = {
                    "id": id,
                    "flagB": 1
            }
            
        response = requests.post(dbURL + "/update_flagb", json=updateData)
        
        await send_results_to_user(context, update.effective_chat.id, prompt, response, sourceList, startTime)
        
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error processing the request!")
        
    
async def redacted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract the argument from the command
    argument = ' '.join(context.args)
    startTime = rolex.now()
    
    notificationMessage = "*Processing prompt:* \n" + argument + "\n\n" + "*Time start: " + startTime.strftime("%Y-%m-%d %H:%M:%S") + " (GMT +7)*"
    # Process the argument as needed
    # For demonstration, just echo back the argument
    await context.bot.send_message(chat_id=update.effective_chat.id, text=notificationMessage, parse_mode='Markdown')
    
    # Make an API call to the queue system
    url = queueURL + "/add_to_queue/"
    headers = {"Content-Type": "application/json"}
    data = {"prompt": argument}
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        response_data = response.json()
        request_id = response_data.get("request_id")
        
        # Start a loop to check for results periodically
        while True:
            # Make an API call to the queue system to get the results
            url = queueURL + f"/get_result/{request_id}"
            response = requests.get(url)
            if response.status_code == 200:
                result = response.json()
                if result.get("gptResult") is not None:
                    await send_results_to_user(context, update.effective_chat.id, argument, result.get("gptResult"), result.get("gptSource"), startTime)   
                    break
            await asyncio.sleep(1)  # Wait for 1 second before checking again
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error processing the request")

async def send_results_to_user(context, chat_id, argument, gptResult, gptSource, startTime):
    
    formattedResponse = "*Replying to:*\n" + argument + "\n" + "*Response:*\n" + gptResult + "\n"
    formattedSource = "*Source:*\n" + gptSource[0] + "\n" + gptSource[1] + "\n"
    endTime = rolex.now()
    
    stopTime = "*Time stop: " + endTime.strftime("%Y-%m-%d %H:%M:%S") + " (GMT +7)*"
    
    diffTime = endTime - startTime
    
    # Assuming diffTime is a timedelta object
    hours, remainder = divmod(diffTime.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format the time taken
    timeTaken = "*Time taken: {:02}:{:02}:{:02} (HH:MM:SS)*".format(int(hours), int(minutes), int(seconds))

    responseMessage = formattedResponse + "\n" + formattedSource + "\n" + stopTime + "\n" + timeTaken
    
    await context.bot.send_message(chat_id=chat_id, text=responseMessage, parse_mode='Markdown')



if __name__ == '__main__':
    application = ApplicationBuilder().token(tokenKey).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)
    
    redacted_handler = CommandHandler('redacted', redacted)
    application.add_handler(redacted_handler)
    
    prompt_handler = CommandHandler('prompt', prompt)
    application.add_handler(prompt_handler)

    
    application.run_polling()