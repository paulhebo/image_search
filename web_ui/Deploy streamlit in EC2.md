# Deploy streamlit in EC2

### 1.Create EC2 instance

Network settings choose "Allow HTTP traffic from the internet"

### 2.Connect to EC2, install the following dependencies:

1. sudo yum update
2. sudo yum install nginx
3. sudo yum install tmux -y
4. sudo yum install python3-pip

### 3.Create nginx profiles

1. cd /etc/nginx/conf.d
2. sudo touch streamlit.conf
3. sudo chmod 777 streamlit.conf
4. vi streamlit.conf

enter the template:

```
upstream ws-backend {
        server xxx.xxx.xxx.xxx:8501;
}

server {
    listen 80;
    server_name xxx.xxx.xxx.xxx;

    location / {
            
    proxy_pass http://ws-backend;

    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header Host $http_host;
      proxy_redirect off;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
    }
  }
```

Change the xxx.xxx.xxx.xxx to the EC2 private IP.


### 4. start nginx：sudo systemctl start nginx.service

### 5.Run streamlit ui stript

1. cd /home/ec2-user/image_search/web_ui
2. tmux
3. streamlit run demo_ui.py

### 6.Open ui page

Enter the url in the webpage：http://<EC2 public IP>
