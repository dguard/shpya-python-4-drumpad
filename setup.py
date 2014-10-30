import swmixer
import json
from pyxhook import HookManager


def handle_event(event):
    if event.Key in watched_keys:
        if not sounds_running.get(event.Key):
            info = sounds[watched_keys.index(event.Key)]
            sounds_running[event.Key] = {
                'snd': swmixer.StreamingSound(info['sound']),
                'status': STATUS_STOP,
                'loops': info['loops'],
                'pause': info['pause']
            }
        sound = sounds_running.get(event.Key)

        if sound['status'] == STATUS_PLAY:
            on_stop(sound)
        else:
            on_start(sound)
    if event.Key == 'Escape':
        exit()


def on_stop(sound):
    if sound.get('pause') and sound.get('loops') != 0:
        sound['chan'].pause()
        sound['is_paused'] = True
        sound['status'] = STATUS_STOP
    else:
        sound['status'] = STATUS_PLAY


def on_start(sound):
    if sound.get('is_paused'):
        sound['chan'].unpause()
    else:
        sound['chan'] = sound['snd'].play(volume=0.5, loops=sound['loops'])

    if sound.get('loops') != 0:
        sound['status'] = STATUS_PLAY
    else:
        sound['status'] = STATUS_STOP


def load_sounds_and_keys():
    with open('sounds.json') as f:
        data = json.loads(f.read())['sounds']

        def parse_sound(x):
            return {
                'loops': x.get('loops', 0),
                'pause': x.get('pause', 0),
                'sound': x['sound']
            }
        return map(parse_sound, data), map(lambda x: x['key'], data)


if __name__ == '__main__':
    STATUS_PLAY = 'play'
    STATUS_STOP = 'stop'

    swmixer.init(chunksize=1024, stereo=True)
    swmixer.start()

    sounds, watched_keys = load_sounds_and_keys()
    sounds_running = {}

    hm = HookManager()
    hm.HookKeyboard()
    hm.KeyUp = handle_event
    hm.start()
    print("\n\nPress \"Escape\" to exit\n\n")