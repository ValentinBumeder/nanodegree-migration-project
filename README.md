# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

| Azure Resource | Service Tier | Monthly Cost |
| ------------ | ------------ | ------------ |
| *Azure Postgres Database* | Burstable | 18.53€ |
| *Azure Service Bus*   | Basic | 0.05€ |
| *Azure App Service* | Basic B1 | 11.62€ |
| *Azure Function App* | Consumption | 0.12€ |

Total costs are estimated to be approx. 30,20€ per month. It has to be considered, that these are the costs for a very basic setup, that will work for a lower number of users. If the app is used very frequently, the ressources might be scaled up and produce higher costs.

## Architecture Explanation
# Azure App Service
The Application is split on two services. The main application is running on a Azure Web Service. 
The alternative for the Web Service would have been to use Virtual Machines, but for a simple application, that does not have computing intensive processes running, using a Azure Web Service is more cost-effective. Furthermore it is easier to maintain, so the maintenance costs are lower than for using virutal machines. 
# Azure Function
The background job of sending out email notifications to all users was split out of the application, since this is a longer running process, that would use lot's of computing power of the Azure Web Service and could lead to errors, if it was too slow. The job is running on a Azure Function App, which is triggered by a Azure Service Bus Queue. The Service Bus Queue is a good way, to counter an overload of the system, since it can buffer a high number of requests to the /notification POST endpoint. Furthermore, the Azure Function is very cost effective, since the costs are based on the consumption of the function. So, in times where no notifications have to be sent out, the function will not produce costs. Furthermore, the Azure Function can be scaled very well.
# Azure Database for PostgreSQL flexible server
The Azure Database for PostgreSQL flexible server is used as service for the database, that has been migrated from the backup. This is a managed database, which leads to the positive affect, that developers can focus on the database structure and do not have to manage updating and securing virtual machines. 
The Azure Database for PostgreSQL flexible server is also very cost effective, since it can be scaled very easily. So for a small number of user, as for example in the current situation, where the application is only used for testing, a very small amount of computing and storage ressources can be selected, in order to save costs. If the usage increases or the application has peaks in the usage, the database can be scaled up, also based on a automated ruleset. By that, a good performance and optimal usage of budget can be ensured.
# Service Bus Namespace
The Azure Service Bus Namespace is used to decouple the sending emails, a typical background job of the application, from the application. Through that, the load of the application is not affected by the long running email sending process. This can resolve the problem of occuring errors, due to an overload of the application. Furthermore the Azure Service Bus is an enabler for scaling. It would be possible to have multiple 'runners' in the background, that pick up the messages from the queue. 
The service bus namespace is basically an enabler to save costs, since application itself doesn't need to be scaled up due to the load of the email sending task. The costs of the function app are based on consumption, so you only pay what you use. Without a service bus, this cost-effective architecture would not be possible. The service bus namespace itself is very cheap and produces only 0.05€ of costs per month. 
# Storage accounts
Both, the function app and the app service use a storage account, which are created with the services automatically and are used for internal Azure functions. Since storage account costs are based on consumption, there are practically no costs incurring from these accounts.
