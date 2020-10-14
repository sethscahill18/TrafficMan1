# Web Application
> Permit a user to share their location in real-time with the traffic management system. 

This project aims to create a method which allows road users to share their location with a traffic management system throughout the journey. The Web App was created as a tool to faciliate this action. The Web App achieved this by performing the following functionality:
1. Web App can be opened on any mobile device which possesses GPS capability.
2. The user must register an account. The Web App enables the user to input their details and sends the information to Firebase for authenification.
3. The user must select the road user option as they wish to share their GPS location. The Web App provides this option to the user and requests access from the user's device to use its GPS capability.
4. The user must commence the sharing of GPS location by confirming the trip has begun. The Web App displays this option to the user and once trip has commenced the Web App will connect to the firebase realtime database and will continuously push the user's GPS location data.
5. At the end of the trip, or at any desired moment, the user must stop sharing location. The Web App displays the option to end the trip during the trip. When slected by the user the Web App will stop sending GPS location data to the firebase realtime database adn will send a signal to the database that the trip has finished.

## Developing

Download the code associated with Web App, this consists of two javascript and one HTML script. 
Open in the code editor which supports Javascript and HTML.
To view the User Interface of the Web App simply run the html script.

To activate the full functionality of the Web App an established Google firebase account is required. Firebase possesses features that enable the creation of a live Web App. The features nesscessary in this case are: user authenification, web hosting service and access to a real-time cloud database. The unique details corresponding to the created firebase account must be input to the HTML script under the section titled "Web app's Firebase configuration unique codes" this will connect the Web App to teh firebase features/services.

# Links

The Web App created to allow a user to share their location in real-time with the traffic management system can be found at the following link: https://webappdatabase3.web.app/

For a mobile device it is adviced to open this link in the Google Chrome App.


