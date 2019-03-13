from blinker import signal


game_finished = signal(
    'game_finished',
    doc='期次完结。sender: game'
)
batch_finished = signal(
    'batch_finished',
    doc='批次完结. sender: batch'
)
