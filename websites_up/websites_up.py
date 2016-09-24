#!/usr/bin/env python
import urllib.request
import smtplib
from socket import timeout
from email.mime.text import MIMEText
from urllib.error import HTTPError
from urllib.error import URLError
import logging
import click


def read_server_settings(path):
    """
    Reads server address, port and login credentials from a file.

    File structure:
    server_address:server_port
    username
    password

    Returns: (host, port, user, passw)
    """
    f = open(path, 'r')
    server_settings = f.readline()
    user = f.readline().rstrip('\n')
    passw = f.readline().rstrip('\n')
    f.close()

    host, port = server_settings.rstrip('\n').split(':')

    return (host, port, user, passw)


def smtp_send(path, receivers, text, subject='Website errors!', html=False):
    """
    Sends a MIMEText msg over the specified SMTP server using starttls.
    Server and user specification retrieved via read_server_settings(path).
    """
    try:
        (host, port, user, passw) = read_server_settings(path)
        msg = compose_msg(user, receivers, text, subject, html)

        s = smtplib.SMTP(host, port)
        s.starttls()
        s.login(msg['From'], passw)
        s.sendmail(msg['From'], msg['To'], msg.as_string())
        s.quit()

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info('Successfully sent e-mail to %s', msg['To'])
    except FileNotFoundError:
        logger.error('Failed to open settings file: %s!', path, exc_info=True)
    except Exception:
        logger.error('An error occured!', exc_info=True)


def compose_msg(sender, receivers, body, subject='Website errors!', html=False):
    """
    Composes a simple MIME Message with the given parameters.
    """
    msg = MIMEText(body, ('html' if html else 'plain'))
    msg['To'] = receivers
    msg['From'] = sender
    msg['Subject'] = subject

    return msg


@click.command()
@click.argument('URLs', type=click.File('r'))
@click.option('--settings', help='Path to file containing mail settings.')
@click.option('--seconds', default=3,
              help='Seconds waiting for answer of the website.')
@click.option('--email', help='E-Mail address to send errors to.')
def check_websites(urls, settings, seconds, email):
    """
    Checks all websites specified in URLs.
    If email is set, errors will be mailed to the given address.
    """
    logging.basicConfig(filename='./websites_up.log', level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())
    logger = logging

    try:
        urls = urls.readlines()
        logger.info('Read URLs from file...')
        errors = []

        for url in urls:
            (status, msg) = check_website(url.rstrip('\n'), seconds)
            if not status:
                errors.append(msg)

        if len(errors) > 0:
            msg_text = '\n'.join(errors)
            if settings:
                if email:
                    smtp_send(settings, email, msg_text)
                else:
                    logger.warn('No mail receiver specified!')
            elif email:
                logger.error('You need to specify a settings file!')
    except FileNotFoundError:
        msg_text = ('Failed to open URLs file: %s!' % (urls))
        logger.error(msg_text, exc_info=True)
        if settings:
            if email:
                smtp_send(settings, email, msg_text)
            else:
                logger.warn('No mail receiver specified!')


def check_website(url, seconds):
    """
    Pulls a website with a given timeframe to see if it's online.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info('Trying to pull %s (timeout=%s)', url, seconds)
    try:
        urllib.request.urlopen(url, timeout=seconds).read()
    except (HTTPError, URLError) as error:
        msg = ('Data of %s not retrieved! %s' % (url, error))
        logging.error(msg)
        return (False, msg)
    except timeout:
        msg = ('%s timed out!' % (url))
        logging.error(msg)
        return (False, msg)
    else:
        msg = ('Successfully pulled %s.' % (url))
        logging.info(msg)
        return (True, msg)


if __name__ == '__main__':
    check_websites()
