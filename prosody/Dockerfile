FROM prosody/prosody

RUN prosodyctl cert generate localhost
RUN chown root:prosody /etc/prosody/certs/localhost.key
RUN chmod 640 /etc/prosody/certs/localhost.key
RUN prosodyctl register load_generator localhost pwd
RUN prosodyctl register crossroad_handler localhost pwd
RUN prosodyctl register waiting_handler localhost pwd