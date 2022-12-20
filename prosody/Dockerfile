FROM prosody/prosody

RUN prosodyctl cert generate localhost
RUN chown root:prosody /etc/prosody/certs/localhost.key
RUN chmod 640 /etc/prosody/certs/localhost.key
COPY config/prosody.cfg.lua /etc/prosody/prosody.cfg.lua
