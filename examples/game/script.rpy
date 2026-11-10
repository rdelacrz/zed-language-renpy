# A small editor fixture; no Ren'Py SDK or image/audio assets are required to parse it.
define e = Character("Eileen", color="#c8ffc8")
default score = 0
default inventory = {"apple": 1}
image bg room = "room.png"

init python:
    def greeting(name):
        values = [
            "こんにちは",
            name,
        ]
        return " ".join(values)

init:
    define narrator = Character(None)

transform fade_in:
    alpha 0.0
    linear 0.5 alpha 1.0

screen hud():
    vbox:
        text "Score: [score]"
        textbutton "Continue" action Jump("chapter_two")

style dialogue_text is default:
    size 24
    color "#ffffff"

label start:
    scene bg room
    show screen hud
    e "Hello, {b}world{/b}! [score] points."
    menu:
        "Continue" if score >= 0:
            $ score += 1
            jump chapter_two
        "Wait":
            if score > 0:
                e "Waiting."
            else:
                pass
    $ renpy.pause(0.5)
    return

translate french strings:
    old "Continue"
    new "Continuer"
