# YouTrack

### A sesam-connector for YouTrack. 

It can be used to import  issues, users, roles and projects.

**An example of system config**   
```
{
  "_id": "<Name of your system i.e youtrack>",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "LOG_LEVEL": "INFO",
      "token": "<Token to access YouTrack>"
    },
    "image": "sesamcommunity/youtrack:latest",
    "port": 5000
  },
  "verify_ssl": true
}
```
 
**An example of input pipe config for incremental issues import**  
   ```
   {
  "_id": "<Name of your pipe i.e youtrack-issues>",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "<name of your system>",
    "is_chronological": true,
    "supports_since": true,
    "url": "/issues"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"]
      ]
    }
  }
}

```

**An example of input pipe config to import users, roles, projects**  
   ```
{
  "_id": "<Name of your pipe i.e youtrack-users>",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "<name of your system>",
    "url": "/<users or roles or  projects, depending what kind of list, you want.>"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"]
      ]
    }
  }
}

```

 
