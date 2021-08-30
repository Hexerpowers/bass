# BASS (eng: окунь)

> Если оно не видит людей, значит таков путь...


## Для использования необходимы библиотеки: 

```shell
sudo apt update
sudo apt upgrade
sudo apt install libopencv-dev
sudo pip3 install opencv-python
sudo pip3 install pymavlink
sudo curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
```

а так же переменная среды MAVLINK20=1

## Для установки используем (обязательно!):
```shell
git lfs install
git clone https://github.com/Hexerpowers/bass
```

## Для запуска используем
```shell
python3 run.py
```

## Конфигурация приложения:

```shell
nano cfg/bass.cfg
```

```shell
[yolo]
model_src = yolo-cfg/v4-tiny/2kv/main_v4_tiny_6000.weights
    > Путь до файла с тренированными весами для выбранной модели
cfg_src = yolo-cfg/v4-tiny/main_v4_tiny.cfg
    > Путь до конфигурационного файла YOLO (тот же, что и при тренировке)
names_src = yolo-cfg/obj.names
    > Путь до файла с именами классов, можно заменить массивом в коде
size = 608
    > Разрешение картинки, подаваемой на вход нейросети
scale = 256
    > MAGIC

[mavlink]
address=localhost
    > Адрес узла, к которому будет подключаться клиент
port=14540
    > Порт, на который будет подключаться клиент
protocol=udpout
    > Протокол. В нашем случае либо udpout либо tcpout

[bass]
use_timecodes = 1
    > Выводить ли в консоль время инициализации приложения и проверки каждого кадра
use_mavlink = 0
    > Использовать ли модуль мавлинка
use_display = 1
    > Выводить ли картинку на экран (в случае, если он подключён)    
mode = stream
    > Режим работы. Значения: stream или image. В случае с image, берёт тестовую
    > картинку по указанному source. В случае stream, подгружает видеопоток
    > из source: либо видеофайл, либо камера, либо IP камера по rtsp
source = test/01.mp4
    > Либо путь до тестового изображения или видеофайла, либо строка подключения к 
    > IP камере вида
    > rtsp://admin:admin@192.168.31.10:554/DeskCamera/webcam1
```
