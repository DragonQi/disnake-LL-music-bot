# disnake-LL-music-bot
## музыкальный бот, запрограммированный на питоне, с интерактивным плеером, командами слэш/слэш и т. д. Использование библиотек disnake и wavelink/lavalink.

### Algumas previews:

- Для работы с ботом используйте / команды

![](https://media.discordapp.net/attachments/554468640942981147/944942596814426122/unknown.png)

- Player controller: normal/mini-player (skin: default_progressbar)

![](https://media.discordapp.net/attachments/554468640942981147/944942948406153276/unknown.png)

- Player controller: fixed/extended with song requests channel and conversation (skin: default_progressbar), configurable with command: /setup

![](https://media.discordapp.net/attachments/554468640942981147/944945573834936340/unknown.png)

- Player controller: song-request em canal de forum (múltiplos bots) e skin embed_link.

![](https://media.discordapp.net/attachments/554468640942981147/1019806568134475786/forum_song_request.png)

* Есть несколько других скинов, посмотрите их все с помощью команды /change_skin (вы также можете создать другие, используйте шаблоны по умолчанию, которые находятся в папке [skins](utils/music/skins/) в качестве эталона, создайте копию с другим имя и изменить свой вкус).

## Протестируйте своего собственного бота прямо сейчас с этим источником, развернув его в одном из следующих сервисов:

---

<details>
<summary>
Repl.it
</summary>
<br>

[![Run on Repl.it](https://replit.com/badge/github/zRitsu/disnake-LL-music-bot)](https://replit.com/new/github/zRitsu/disnake-LL-music-bot)

* 1 - После нажатия кнопки выше дождитесь завершения развертывания.
* 2 - Перейдите к секретам (замок на левой панели) и создайте секрет с именем TOKEN и в качестве значения поместите токен бота (если у вас его нет, посмотрите, как его получить с помощью этого руководства [учебник] (https:/ /www.youtube.com/watch?v=lfdmZQySTXE)).
* 3 - Я также настоятельно рекомендую использовать mongodb для базы данных вместо json, для этого создайте ключ с именем MONGO и в значении укажите ссылку на ваш URL-адрес mongodb (если у вас его нет, посмотрите, как получить его через это [ учебник](https://www.youtube.com/watch?v=x1Gq5beRx9k)). </br>
  `при желании вы можете изменить другие конфиги, см. файл .env-example`
* 4 - Нажмите «Выполнить» (кнопка **play**) и подождите, пока бот установит зависимости и запустится.
</details>

---

<details>
<summary>
Render.com
</summary>
<br>

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/zRitsu/disnake-LL-music-bot/tree/main)

* 1 - В поле **TOKEN** введите токен бота **( [инструкция по получению](https://www.youtube.com/watch?v=lfdmZQySTXE) )**.
* 2 - В поле **DEFAULT_PREFIX** указать префикс для бота.
* 3 - В полях **SPOTIFY_CLIENT_ID** и **SPOTIFY_CLIENT_SECRET** введите свои ключи Spotify **( [руководство по получению](https://www.youtube.com/watch?v=ceKQjWiCyWE))* *.
* 4 - В поле **MONGO** поместите ссылку на вашу базу данных MongoDB **( [руководство по получению](https://www.youtube.com/watch?v=x1Gq5beRx9k) )**.
* 5 - Нажмите Применить и дождитесь процесса сборки, пока бот не запустится (это может занять много времени, не менее 13 минут или более, чтобы завершить развертывание + запуск бота + запуск сервера lavalink).
</details>

---

<details>
<summary>
Railway
</summary>
<br>

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/WbAx7d?referralCode=JDUKpu)
* 1 - Заполните данные, которые будут запрошены на следующей странице (обязательны отмеченные красными звездочками).
* 2 - Нажмите кнопку развертывания и дождитесь завершения развертывания (зеленый цвет. Может пройти несколько секунд, прежде чем развертывание появится в списке).
* **Примечание 1:** Требуется учетная запись github с хорошим временем сборки или кредитная карта для подтверждения учетной записи.
* **Примечание 2:** Если вы хотите изменить конфигурации, используемые на шаге 1, щелкните переменные и создайте/измените ключ и желаемое значение конфигурации, обратитесь к файлу .env-example, чтобы просмотреть все доступные конфигурации.
</details>

---

<details>
<summary>
Gitpod
</summary>
<br>

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/zRitsu/disnake-LL-music-bot)

* 1 - Откройте файл .env и поместите токен бота в соответствующее поле (если у вас его нет, посмотрите, как его получить с помощью этого руководства [tutorial](https://www.youtube.com/watch? v=lfdmZQySTXE) как получить). Я также настоятельно рекомендую использовать mongodb, найдите, где у вас есть MONGO= в файле .env, и поместите в него ссылку на вашу базу данных mongodb (если у вас ее нет, посмотрите, как получить ее через этот [учебник] (https ://www.youtube.com/watch?v=x1Gq5beRx9k)).
* 2 - Щелкните правой кнопкой мыши файл main.py и выберите «Запустить файл Python в терминале».
* **Примечание 1:** Не забудьте перейти к списку [рабочих областей] (https://gitpod.io/workspaces) и щелкнуть 3 точки проекта, а затем нажать **закрепить**. `(это предотвратит удаление рабочего пространства после 14 дней бездействия)`
* **Примечание 2:** Не используйте gitpod для размещения/поддержания бота в сети, он для этого не подходит!
</details>

---

<details>
<summary>
Heroku
</summary>
<br>

[![Heroku_Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/zRitsu/disnake-LL-music-bot/tree/main)

**Примечание. С 28 ноября 2022 г. heroku больше не будет предоставлять бесплатные планы ([нажмите здесь](https://blog.heroku.com/next-chapter), чтобы узнать больше).*** 1 - Заполните данные, которые будут запрошены на следующей странице
* 2 - Нажмите «Развернуть приложение» и подождите (процесс может занять от 2 до 5 минут).
* 3 - Нажмите «Управление» и перейдите к ресурсам.
* 4 - Отключите веб-дино и включите автообновление (или быстрое исправление, не включайте оба одновременно!) И подождите, пока бот войдет в систему. `(в верхнем углу нажмите больше и просмотрите журналы, чтобы следить за журналами)`
* **Примечание:** Если вы хотите изменить конфиги, использованные на шаге 1, перейдите в настройки и нажмите Reveal Config Vars, создайте/измените ключ и желаемое значение конфига, см. файл .env-example для просмотреть все доступные конфиги.
</details>

---

<details>
<summary>
Хостинг на собственном ПК/VPS (windows/linux)
</summary>
<br>

### Requisitos:

* Python 3.8 ou superior:<br/>
[Download pela Microsoft Store](https://apps.microsoft.com/store/detail/9PJPW5LDXLZ5?hl=pt-br&gl=BR) (Recomendável para usuários do windows 10/11).<br/>
[Download direto do site oficial](https://www.python.org/downloads/) (Marque esta opção ao instalar: **Add python to the PATH**)
* [Git](https://git-scm.com/downloads) (Não escolha a versão portable)</br>

* [JDK 11](https://www.azul.com/downloads) ou superior (Windows e Linux x64 é baixado automaticamente)</br>

`Примечание. Для нормальной работы этого источника требуется не менее 512 МБ ОЗУ И 1 ГГц ЦП (если вы запускаете Lavalink на том же экземпляре бота, учитывая, что бот является частным).`

### Запустить бота (краткое руководство):

* Загрузите этот исходник как [zip] (https://github.com/zRitsu/disnake-LL-music-bot/archive/refs/heads/main.zip) и распакуйте его (или используйте команду ниже в терминале/cmd а затем откройте папку):```shell
git clone https://github.com/zRitsu/disnake-LL-music-bot.git
```
* дважды щелкните файл setup.sh (или просто настройте, если ваши окна не отображают расширения файлов) и подождите.</br>
  `Если вы используете Linux, используйте команду в терминале:`
```shell
bash setup.sh
```
* Появится файл с именем **.env**, отредактируйте его и поместите токен бота в соответствующее поле (вы также можете редактировать другие вещи в этом же файле, если хотите внести определенные изменения в бота).</br >
  `Примечание. Если вы не создали учетную запись бота,` [см. это руководство](https://www.youtube.com/watch?v=lfdmZQySTXE), `чтобы создать своего бота и получить необходимый токен.`</br >`Я также настоятельно рекомендую использовать mongodb, найдите, где у вас есть MONGO= в файле .env, и поместите в него ссылку на вашу базу данных mongodb (если у вас ее нет, посмотрите, как получить ее из этого` [ учебник](https://www.youtube.com/watch?v=x1Gq5beRx9k)`). `
* Теперь просто откройте файл run.sh, чтобы запустить бота (если вы используете Linux, используйте команду ниже):
```shell
bash run.sh
```

### Notas:

* Чтобы обновить бота, дважды щелкните файл update.sh (Windows), для Linux используйте команду оболочки/терминала:
```shell
bash update.sh
```
`При обновлении есть шанс, что любые сделанные вручную изменения будут потеряны (если не форк этого исходника)...`<br/>

`Примечание. Если вы запускаете исходный код непосредственно с компьютера с Windows (и на котором установлен git), просто дважды щелкните файл update.sh`</details>

---

Примечание: на [wiki]((https://github.com/zRitsu/disnake-LL-music-bot/wiki) есть еще несколько руководств).

### Важные заметки:

* Этот источник был создан с целью использования частных ботов (он недостаточно оптимизирован для обработки высоких запросов сервера).

* Рекомендую использовать текущий исходник без изменений кода, выходящих за рамки текстов. Если вы хотите внести изменения (и особенно добавить новые функции), настоятельно рекомендуется иметь знания о python и disnake. И если вы хотите, чтобы ваш исходник модифицировался с обновлениями в днях, используя базовый исходник, я также рекомендую иметь знания в git (по крайней мере, достаточно, чтобы сделать слияние без ошибок).

* Если вы хотите сделать видео/учебник, используя этот источник, вы можете совершенно свободно использовать его для этой цели, если он соответствует [лицензии](/LICENSE) (и если вы хотите помочь мне, сохраните исходные титры в коде появляются только в команде /about)
