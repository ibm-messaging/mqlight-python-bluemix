# IBM MQ Light Python Fish Alive Sample

This project contains Python samples demonstrating how to use the MQ Light
Service for Bluemix to write cloud apps which can perform worker offload.

Check out the blog posts at [IBM Messaging](https://developer.ibm.com/messaging/blogs/)
for more info on these samples.

## Deploying to Bluemix

The sample can be used with the 'Message Hub' service.

1.  Create an instance of the service using either the Bluemix console or the
    Bluemix cf command line tool.

2.  In the Message Hub service Dashboard, create a topic called "MQLight" with a single partition.

3.  Edit the manifest.yml file in the root directory of the sample to reflect
    the name of the service created above.

 ```yml
   services:
   - <TheNameOfYourService>
 ...
   services:
   - <TheNameOfYourService>
 ```

4. From the root directory of the sample use the Bluemix cf command line
   tool to push the sample to Bluemix, as below:
 ```
 $ cf push
 ```

For further information about Bluemix command line tooling, see
[IBM Bluemix Command Line Tooling](https://www.ng.bluemix.net/docs/starters/install_cli.html)

