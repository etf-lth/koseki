![Koseki Logo](https://raw.githubusercontent.com/etf-lth/koseki/master/koseki/themes/koseki/img/logo.png)

# 👪 **Koseki**

Koseki is a micro and lightweight web-based membership system. It features basic functionalities such as member enrollment by staff, member login, fee registration, automatic fee reminder emails and membership expiration emails. The application is designed for small to medium sized organisations and features simple configuration and an easy permission system to quickly get started.

The word "Koseki" (戸籍) is Japanese for "family registry". The system was originally developed back in 2012, for the Student's Association for Applied Electronics ("ETF") at the Faculty of Engineering, Lund University, Sweden. The system has since been upgraded and rewritten allowing for a fresh, secure and welcoming environment. Generalisation, modularity and configurability opens up the posibility for other organisations to use this system as well. Note that no **official** support is given.

## 🔰 **Installation**

Koseki requires Python 3.9 or above. For production it also requires a MySQL or MariaDB server, although can run on SQLite for testing purposes.

To install the dependencies neccesary, please run:

```bash
sudo python3 -m pip install -r requirements/production.txt
```

You can also install Koseki as a system service in SystemD. Please move or place the Koseki installation at `/srv/koseki`, then make a symlink to the service file. Please configure Koseki before starting it...

```bash
sudo chown root:root /srv/koseki -R
sudo chmod 770 /srv/koseki -R
sudo ln -s /srv/koseki/koseki.service /etc/systemd/system/koseki.service

sudo systemctl enable koseki
sudo systemctl start koseki
sudo systemctl status koseki
```

It is possible to view the log by tailing the `koseki.log` file in the installations folder. It is also possible to run the system mantually (for example in a Tmux session, although this is discouraged due to no restart if machine reboots) with the `./start_production.sh` command.

## 🏠 **Configuration**

An minimal example file is provided at `koseki.cfg.templ`. An expansive list of all available configuration options can be found by looking in `koseki/config.py` (To do: Create Wiki documentation).

Copy the `koseki.cfg.templ` file to `koseki.cfg` before starting the system. Once started and connected to a database it will automatically create all neccesary tables and pre-populate it with the required data for you.

The default login credentials are:

| Username          | Password |
| ----------------- | -------- |
| admin@example.com | password |

⚠️ **Please change the default password and email after login!!!** ⚠️ 

## ♻️ **Updates & Support**

Please note that this software is still lacking generalisation features, for example changing currency (which is still hard-coded to Krona "kr" only). See [**Issues**](https://github.com/etf-lth/koseki/issues) for a more detailed to-do list.

Due to this being a student-driven project, no official/deadline-driven support can be given. Please contact whoever is DDG (IT-role) at the association and ask nicely. :-)

## 💮 **Development**

Standard development environment is VSCode. Please install the development dependencies with:

```bash
python3.9 -m pip install -r requirements/development.txt
```

All commits must follow PEP 8, pass pylint, pass pytests and be coded with "future-proof" in mind. Keep in mind to make features "organisation agnostic" i.e. configurable, and to make it toggable (by making it into a Plugin) if it falls outside the core features of Koseki.

## 📠 **Support & Legal**

ETF takes absolutely no responsability for anything this software is used for, or actions caused by this software, or actions caused by users using this software. This is not legal advice, we are engineering students. Good luck.
