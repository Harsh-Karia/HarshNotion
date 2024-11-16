## Program Description: 
This program is a simulated email client that is built on top of Notion's API. IT allows users to send and receive messages from other users in the database. Users can also tag an email into three categories: work, social, and promotions, similar to modern email systems. This allows for efficient inbox management and email filtration. This user-specific tagging system was implemented in a way that one user tagging an email would not affect how other users see that email. This allows for a personalization feature so only users that tagged an email will see the tag being applied for that email. There is also an option to view the sent emails to see the emails that a user may have sent previously. This feature is private which means users can only view their own sent messages. On the other hand, only  recipients of emails can delete messages. Along with this, there is a separate file that contains the mock unit-tests for this program, which comprehensively cover all of the various program functionalities while simulating the Notion API.


## Product and Technical Choices and Why:
I decided to take the slightly unconventional route and chose to develop in **Python** because I realized that the features I needed to manipulate the `message` field quite a bit, which was the most-straightforward in **Python**. However, to test out the Notion API and integrations, I initially did a quick run-through of the official `JavaScript SDK` and ran it on a test integration.
- While creating this product, I focused on making it seamless and intuitive for a potential customers. I thought back to how I use emails and I realized that I often tag my emails and decided to implement it without any structural database changes.
- A key technical choice that I made was having the message field handle multiple features without making structural database changes. This meant I went through multiple iterations of tag parsing but gave some valuable programming insights. 
    - When I first implemented the tag feature, I only added specific tags which prevent emails from appearing in the general inbox. So I implemented a default general tag for every email. But upon testing, I realized that senders were able to see what emails the recipients tagged. So I made it so that the tag would appear in the format `[social:user1]` to maintain personalization. I also added  redundancy restricting tagging to recipients only. This was a great learning experience for me because it allowed me to think of vast number of scenarios that a potential user could face and write my code to account for them adequately.

## Future Improvements:
There are many future improvements but a majority of them can be implemented by modifying the database structurally. 
- As someone interested in cybersecurity, I realized that authentication is basically nonexistent in this program. I would want to allow users to have a login flow that can protect their emails and keep them private.
- I want to introduce a delay of 15-30 seconds between when the sender sends an email and when the recipient receives an email. This would be beneficial because then I can allow senders to delete an email for a short time frame after sending the email in case they change their mind. 
- And the last two functionalities that would be nice to have are an untag functionality and a delete-all-messages option. Currently there is no untag support in my program and if I delete an email, it removes the email from the database completely instead of just removing it from the user's account. This would mean that if a recipient decides to delete an email, then a sender would have no record of ever sending that email, which I would like to fix. 




## Setup Process:
1. **Install Dependencies**  
   Install the required Notion client library:
   ```bash
   pip install notion-client
   
2. **Change Keys**  
   Modify the `config.py` file with your own API key and database ID if needed.

1. **Running Mail Client**  
   To run the mail client, type:
   ```bash
   python main.py
   ```
   To run the tests, you can use
    ```bash
    python new_tests.py
    ```


## References: 
- https://developers.notion.com/reference/post-database-query
- https://developers.notion.com/docs/authorization
- https://github.com/ramnes/notion-sdk-py
- https://developers.notion.com/docs/create-a-notion-integration#getting-started