import argparse
import collections
import glob
import re
import sys
from pathlib import Path

from jinja2 import BaseLoader, Environment, Template

parser = argparse.ArgumentParser()


def filter_chars(s):
    return re.sub(r'-|/|,', ' . ', s)


parser.add_argument(
    "-d",
    "--dir",
    help="directory containing files to create playlist from",
    default='.')
args = parser.parse_args()

start_dir = Path(args.dir)
playlist_path = start_dir.joinpath(f'{start_dir.name}.m3u')

lst = sorted(glob.iglob(f'{start_dir}/**/*.mp4', recursive=True))
if len(lst) == 0:
    sys.exit(0)

lst2 = []
env = Environment(loader=BaseLoader)
env.filters['filter_chars'] = filter_chars
tpl = env.from_string("""{#- jinja2 -#}
#EXTM3U
{%- for media in lst %}
#EXTINF:-1,{{ media.parent|filter_chars }} {{ media.relative_path|filter_chars }}
{{ media.relative_path }}
{%- endfor %}
""")

Media = collections.namedtuple('Media', 'fname relative_path path parent')
for path in lst:
    path = Path(path)
    media = Media(
        relative_path=str(path.relative_to(start_dir)),
        fname=path.name,
        parent=path.parents[1].name,
        path=path)
    lst2.append(media)

open(playlist_path, 'w').write(tpl.render(lst=lst2))
print(f'created {playlist_path}')
