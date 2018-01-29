FROM docker.elastic.co/beats/filebeat:6.1.2
USER root

COPY filebeat.yml /usr/share/filebeat/filebeat.yml
RUN chown filebeat /usr/share/filebeat/filebeat.yml

RUN mkdir /var/log/audit && chown filebeat: /var/log/audit

USER filebeat
