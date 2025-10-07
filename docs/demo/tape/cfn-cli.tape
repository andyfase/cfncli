# VHS documentation
#
# Output:
#   Output <path>.gif               Create a GIF output at the given <path>
#   Output <path>.mp4               Create an MP4 output at the given <path>
#   Output <path>.webm              Create a WebM output at the given <path>
#
# Require:
#   Require <string>                Ensure a program is on the $PATH to proceed
#
# Settings:
#   Set FontSize <number>           Set the font size of the terminal
#   Set FontFamily <string>         Set the font family of the terminal
#   Set Height <number>             Set the height of the terminal
#   Set Width <number>              Set the width of the terminal
#   Set LetterSpacing <float>       Set the font letter spacing (tracking)
#   Set LineHeight <float>          Set the font line height
#   Set LoopOffset <float>%         Set the starting frame offset for the GIF loop
#   Set Theme <json|string>         Set the theme of the terminal
#   Set Padding <number>            Set the padding of the terminal
#   Set Framerate <number>          Set the framerate of the recording
#   Set PlaybackSpeed <float>       Set the playback speed of the recording
#   Set MarginFill <file|#000000>   Set the file or color the margin will be filled with.
#   Set Margin <number>             Set the size of the margin. Has no effect if MarginFill isn't set.
#   Set BorderRadius <number>       Set terminal border radius, in pixels.
#   Set WindowBar <string>          Set window bar type. (one of: Rings, RingsRight, Colorful, ColorfulRight)
#   Set WindowBarSize <number>      Set window bar size, in pixels. Default is 40.
#   Set TypingSpeed <time>          Set the typing speed of the terminal. Default is 50ms.
#
# Sleep:
#   Sleep <time>                    Sleep for a set amount of <time> in seconds
#
# Type:
#   Type[@<time>] "<characters>"    Type <characters> into the terminal with a
#                                   <time> delay between each character
#
# Keys:
#   Escape[@<time>] [number]        Press the Escape key
#   Backspace[@<time>] [number]     Press the Backspace key
#   Delete[@<time>] [number]        Press the Delete key
#   Insert[@<time>] [number]        Press the Insert key
#   Down[@<time>] [number]          Press the Down key
#   Enter[@<time>] [number]         Press the Enter key
#   Space[@<time>] [number]         Press the Space key
#   Tab[@<time>] [number]           Press the Tab key
#   Left[@<time>] [number]          Press the Left Arrow key
#   Right[@<time>] [number]         Press the Right Arrow key
#   Up[@<time>] [number]            Press the Up Arrow key
#   Down[@<time>] [number]          Press the Down Arrow key
#   PageUp[@<time>] [number]        Press the Page Up key
#   PageDown[@<time>] [number]      Press the Page Down key
#   Ctrl+<key>                      Press the Control key + <key> (e.g. Ctrl+C)
#
# Display:
#   Hide                            Hide the subsequent commands from the output
#   Show                            Show the subsequent commands in the output

Output cfn-cli.gif

## Any tools needed
Require echo
Require cfn-cli
Require jq
Require vim

## Set shell and sizing and font
Set Shell "bash"
# Set FontFamily "Monoflow"
Set FontSize 16
Set Width 1200
Set Height 900
Set Padding 20
Set WindowBar Colorful

## We speed up the output so were not waiting so long for cloudformation
Set TypingSpeed 0.1
Set PlaybackSpeed 3.0
Set CursorBlink false


### Sets PS1 so we dont leak local shell dir
Hide
Type 'PS1="> "' Enter
Type "clear" Enter
Sleep 100 ms
Show

# Type 'echo "StackID: arn:aws:cloudformation:us-west-2:433468561249:stack/prod-lambda/1e7a9d60-95a5-11f0-abec-02b46572ab13"' Sleep 500ms Enter
# Sleep 500ms

## Create Changeset
Type "cfn-cli -s prod.lambda stack changeset create --store" Sleep 500ms  Enter
Wait@120s ## wait for prompt (command completion)

Sleep 18000ms ## Num dependant on PlaybackSpeed

## Clear Screen
Type "clear" Enter
Sleep 500ms

## Execute Changeset
Type "cfn-cli -s prod.lambda stack changeset exec" Sleep 500ms  Enter
Wait@120s ## wait for prompt (command completion)

Sleep 9000ms ## Num dependant on PlaybackSpeed
