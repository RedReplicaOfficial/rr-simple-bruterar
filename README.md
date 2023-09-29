# RR's Simple BruteRAR

Note: This is a proof of concept. It 100% works in a Windows 11 Virtual Python Environment, so I don't see any problem elsewhere too. Make sure dependencies are installed.

Bruteforces the password of a file with .RAR extension. Very minimalistic UI and build, but works perfectly (as far as I know) The maximum password length is limited to 14, and it will use every possibility using "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" charset.

You may freely edit the code, if you know the password length, change it to that, it will be way faster to aquire the password. Also edit the charset if you would like.

The 2.0 version will have the ability to add keyword list, be approx. 8x faster, and it will also include more extensions.

I may add other Quality of Life (QoL) changes in the future if I come up with them or I get suggested about them. ALL, EVERY suggestion OR idea is welcome!

As far as I know I fixed every possible bug I could find and recreate, but if you do find something, please don't hesitate to tell me.

Key Features:

1. Main featuer is obviously cracking .RAR files when the password is lost
2. Password length is set to 14, but can be modified in the code easily
3. Systematically bruteforces, see current charset
4. Currently supports letters, capial letters, and numbers, see charset
5. Logs everything into an external log file. Logging is also visible inside the program.

Implemented:

1. Clock, Avg. Tries/Min, Avg. Tries/Hour implemented. !!!Logging of these does not work fully yet and is bugged!!!
2. "Start" button is now greyed out until P/R system is implemented.

Will be added:

- Pausing and resuming the cracking
- Support for special characters too (ex, !, $, &, etc.)
- Suppoer for wordlists
- Way faster technique
- More extensions to bruteforce through
- Even though this is a hobby program, niche, small, and very young, multiple languages will be available
