# Music Database

Music Database is a locally deployed database to catalog your music collection.

## Installation

Installing base dependencies.

```bash
sudo apt-get -y update
sudo apt-get -y install python3, python3-venv python3-dev
sudo apt-get -y install supervisor nginx git
```

Clone the repository on your machine.

```bash
https://github.com/FionaEff/music_database.git
```

Navigate into the created folder and create a virtual environment.
Then install the required dependencies.
```bash
cd music_database
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Install the Gunicorn webserver for Python web application.s

```bash
pip install gunicorn
```

Create an .env file inside the music_database directory for storing environment variables.

```bash
SECRET_KEY=b35d193614fc47178879331eb8387946
```

You can create your own randomly generated secret key using the following command:

```bash
python3 -c "import uuid; print(uuid.uuid4().hex)"
```

To start Music Database, use the following command:
```bash
gunicorn -b localhost:8000 -w 4 music_database:app
```

Configure the supervisor utility to automatically restart the server, should it crash or the machine be restarted.
Create the conf file called music_database.conf in /etc/supervisor/conf.d with the following content:

```bash
[program:music_database]
command=/home/<username>/music_database/venv/bin/gunicorn -b localhost:8000 -w 4 music_database:app
directory=/home/<username>/music_database
user=<username>
autostar=true
autorestart=true
stopasgroup=true
killasgroup=true
```

After creating this configuration file, you have to reload the supervisor service.

```bash
sudo supervirsorctl reload
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)