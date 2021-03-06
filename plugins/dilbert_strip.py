from __future__ import unicode_literals, division, absolute_import
import logging

from requests.exceptions import RequestException

from flexget import plugin
from flexget.event import event
from flexget.utils.soup import get_soup

log = logging.getLogger('dilbert_strip')


class DilbertStrip(object):

    schema = {'type': 'boolean'}

    def on_task_filter(self, task, config):
        if not (config and task.entries):
            return
        for entry in task.entries:
            if entry.rejected or not (entry['url'].startswith('http://dilbert.com') or \
                                      entry['url'].startswith('http://feed.dilbert.com')):
                continue
            try:
                page = task.requests.get(entry['url'])
            except RequestException as err:
                log.error("RequestsException opening entry '%s' link: %s" % (entry['title'], err))
                continue
            soup = get_soup(page.text)
            try:
                node = soup.find('div', attrs={'class': 'STR_Image'}).find_all('img')[0]
            except Exception as err:
                log.error('Unable to get image node: %s' % err)
                continue
            if node and node.get('src'):
                entry['original_url'] = entry['url']
                entry['url'] = 'http://dilbert.com' + node.get('src')
            else:
                log.error('Unable to get image node for "%s"' % entry['title'])


@event('plugin.register')
def register_plugin():
    plugin.register(DilbertStrip, 'dilbert_strip', api_ver=2)
