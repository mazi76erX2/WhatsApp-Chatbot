# WhatsApp-Chatbot
A FastAPI application that could be used to simulate the Employer Web Portal, and handle the scheduling and distribution of announcements.

## Case Study
We have identified an issue in our current system. Employers send announcements to
their employees (1000+) via our WhatsApp chatbot. An employer logs into our system,
types in the announcement (e.g., "Our end of year party is on Saturday evening!") and has
a choice to send it immediately or schedule the announcement to go out at a specific
future time. We have a scheduler (cron job) that runs every 5 minutes to check whether
any announcements need to be sent. However, we have found that some employees are
receiving the same announcements more than once.

## Task

###### Propose at least 2 reasons why employees might be receiving the same announcement more than once.

##### Answer:

1. **Cron Job Overlapping:**
   One reason could be that the cron job responsible for sending announcements is overlapping or running multiple instances simultaneously. If the cron job is scheduled to run every 5 minutes, it's possible that it hasn't completed its execution before the next instance starts. As a result, the same announcement may be sent multiple times to the employees. To address this issue, it's important to ensure that the cron job is properly configured to prevent overlapping. This can be achieved by implementing locking mechanisms or utilizing scheduling tools that handle job concurrency effectively. By ensuring that each instance of the cron job runs exclusively without overlapping, the problem of duplicate announcements can be mitigated.

2. **Lack of Deduplication Mechanism:**
   Another reason for employees receiving the same announcements multiple times could be the absence of a proper deduplication mechanism. This can occur if the system doesn't keep track of sent announcements or if the logic for checking and filtering duplicates is not robust. To prevent duplicate announcements, the system should maintain a record of previously sent messages. When an announcement is scheduled or sent, the system should compare it with the existing records to identify and filter out any duplicates. Implementing proper deduplication logic, such as comparing message content, timestamps, or unique identifiers, can help ensure that employees receive announcements only once.

3. **Employees are changing their
   WhatsApp numbers:**
   If an employee changes their WhatsApp number and then re-registers with the chatbot, the chatbot may not recognize that this is the same employee and may send them the same announcements again.

###### Propose an architecture that could fix this problem.

##### Answer:

1. **Cron Job Overlapping:**
   To address this issue, it's important to ensure that the cron job is properly configured to prevent overlapping. This can be achieved by implementing locking mechanisms or utilizing scheduling tools that handle job concurrency effectively. By ensuring that each instance of the cron job runs exclusively without overlapping, the problem of duplicate announcements can be mitigated.

2. **Lack of Deduplication Mechanism:**
   To prevent duplicate announcements, the system should maintain a record of previously sent messages. When an announcement is scheduled or sent, the system should compare it with the existing records to identify and filter out any duplicates. Implementing proper deduplication logic, such as comparing message content, timestamps, or unique identifiers, can help ensure that employees receive announcements only once.

3. **Employees are changing their
   WhatsApp numbers:**
   To address this issue, the system should maintain a record of previously sent messages. When an announcement is scheduled or sent, the system should compare it with the existing records to identify and filter out any duplicates. Implementing proper deduplication logic, such as comparing message content, timestamps, or unique identifiers, can help ensure that employees receive announcements only once.

###### Propose an architecture that could fix this problem.

##### Answer:
A proposed architecture that could fix the problem of employees receiving the same announcement more than once:

1. **Use a database to track which employees have received which announcements.** This would allow the WhatsApp chatbot to quickly and easily check whether an employee has already received an announcement before sending it to them again.

2. **Use a queue to store scheduled announcements.** This would ensure that announcements are only sent out once, even if the cron job that is responsible for sending them out experiences some type of error.

3. **Use a unique identifier for each announcement.** This would allow the WhatsApp chatbot to easily identify duplicate announcements and prevent them from being sent out.
