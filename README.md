# Social media app Back-end 
Personal project presenting back-end of the application based on twitter functionality. 
(This is NOT Twitter clone)
##  I've created it with:
 * [Django][djangolink]
 * [Django Rest Framework][restframeworklink]
 * [Celery][celerylink] (with [RabbitMQ][rabbitmqlink])
 
 ## Database I used:
 * [PostgreSQL][postgreslink]
 
 All additional extensions and packages can be found in 'requirements.txt'.
 
 ## REST API
 All endpoints are available on `apischema/` url.
 ![](media-readMe/api_schema.gif)
 
 #### Example queries:
 ##### Successful login response
 ![](media-readMe/login_success.png)
 
 ##### User's tweets and shared tweets
 ![](media-readMe/user_tweets.png)
  
  ## News feed
  The news feed endpoint returns response which consists of:
  * Tweets created by followed people and current user itself.
  * Current user's shared posts as well as these shared by followed people.
  * Time stamp of last tweet/shared tweet.
  ###
  The time stamp needs to be passed in 'load more' request so that the server can 
  dispatch appropriate response. Both tweets and shared tweets are sorted from newest to oldest.
  Shared tweets' sort is based on share date not on post date.
  The size of news feed response is declared in the settings file as a NEWSFEED_SIZE property.
  The client has to merge tweets and shared tweets together. However, 
  unlike ordinary sorting this can be made in linear time, which guarantees a fast load 
  on the client's side, while the sorting process is already made on the server side.
  ###### We cannot return tweets and shared tweets as one, because of serializer limitation. Both have a different structure, which brings advantages and disadvantages. I took this approach to simplify the client's management of responses.
 
   
  
  ## Authentication and Permission
  Authentication is based on Tokens.
  This solution was picked for security reasons.
  Default permission allows anybody to use Api, therefore
  users who are not logged in can both look over the 
  profiles of other users and search for phrases they look for.
  However, they don't have access to like/comment/share tweets 
  as well as to create their own ones.
  Logged users have access to their profiled newsfeeds, 
  which contain tweets of users they follow.
  Every request that needs permission has to contain token.
  Users can log in with both emails and usernames.
  App prevents from using '@' and white spaces in the usernames.
  
  ## Hashtag system
  Instead of searching through all posts to find the right ones with given #hashtag,
  server asynchronously creates object of custom data structure 
  which simplifies the subsequent search.
  This solution reduce execution time.
  Endpoint `api/tweet/withhashtag/<str:hashtag>/`.
  
  ## Popularity system
  Every six hours, the server with the help of celery asynchronously searches 
  the last activities of users and 
  finds those with the greatest increase in popularity(followers).
  After that, the data is saved in Singleton like model and 
  served it to the client.
  Endpoint `api/activity/popularusers/`.
  ###
  Endpoint `api/activity/hashtagtrends/` provides hashtags that may interest 
  the current user and the most popular tweet connected with every hashtag.
 
  ## Pagination
  In order to reduce response size of list requests, there was used pagination. 
  It prevents from overloading.
  Every response has link to next/previous page, which can be simply named as
  'load more'. 
  However, newsfeed endpoint takes different approach, the solution is 
  explained in `apischema/`.  
  
  ### Front-end side
  https://github.com/MattSzm/SocialMediaAppFrontend


 [restframeworklink]:https://www.django-rest-framework.org/
 [djangolink]:https://www.djangoproject.com/
 [celerylink]:https://docs.celeryproject.org/en/stable/
 [postgreslink]:https://www.postgresql.org/
 [rabbitmqlink]:https://www.rabbitmq.com/