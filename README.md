# Synacor Challenge

The [Synacor Challenge](http://challenge.synacor.com) is a programming challenge wherein you take the architecture specification defined in the arch-spec file and attempt to build a VM that can run the self-testing bin file provided.

It should be noted that this project contains massive spoilers. Seriously don't go digging through this source if you want to try the challenge out for yourselves.

# Project Log

## Friday, March 14th, 2014

### 17:33 MDT

Careful inspection of the architecture leaves me with little questions. I'll start as the arch-spec doc suggests and get things going. 

### 21:34 MDT

Wife has called me to bed, I have the first part working but stuck at an infinite loop.... not sure how to get this going. I think I may have to build a debugger too. Perhaps an observer pattern.

## Saturday, March 15th, 2014

### 10:45 MDT

Start off the day getting that debugger going. Using a pub-sub model it was easy to get the vm to publish events and the debugger to hook into them. Time to build commands in for modifying the vm's state

### 13:13 MDT 

Crap, I have a party in less than an hour and no drinks or snacks. Have to side table for now. I have most of the necessary commands in plus some I think I'll need. I can step through and modify registers, the stack, and memory. A good start I'd say. Also got tired of reading large numbers to decipher registers, started adding the annotation '''@X''' where X is the register number 0 - 7.

### 22:30 MDT

OK, I think I've got things going as I need them too, I can get through most of the beginning operational tests. Time for bed.

## Sunday, March 16th, 2014

### 08:00 MDT

Alright, obviously I'm having issues debugging a couple of instructions. I've avoided it long enough, time to build a decompiler. 

### 08:30 MDT

Cool, lots of insight into the code now, easier to follow along with the debugger. Source stashed in challenge.txt for now. Adopted my register annotation to the decompiler since reading it without is a bit painful.

### 12:11 MDT

About to leave for a family thing, last update. **FRUSTRATED** I have an infinite loop and don't know why. I jump to offset 2125, things move smoothly and then I end up looped back to 2125. Very frustrating. Perhaps my bitwise operators aren't correctly accounting for the 15-bit numbers???


### 17:34 MDT

Got back and worked for the last couple of hours seriously trying to find fault in the bitwise operators. I can't find one. Stepping through, testing it out in the interactive shell in isolation... once I get to [2125] (my offset in memory annotation, btw) I end up jumping back to a point in memory that leads to me back at 2125. I'm going to give up for now. I think I need some time to think about the problem. Perhaps the fact that I'm at [2125] is the problem to begin with. Means I've have to backtrack a bit up the stack... sadness.

## Monday, March 17th, 2014

### 14:13 MDT

Spoke with the project creator, he says I'm really close just have to find out why the loop condition isn't being met, now I just have to wait 45 minutes for the day to end...

### 15:06 MDT

And now the real fun beings, first I'll begin by examining the call stack while in that loop. Shouldn't be too difficult since I have the ability to not only set breakpoints on offsets but also execution steps.

### 16:50 MDT

He was a sneaky bastard, hiding a simple loop to 30,050 behind a wall of very expensive operations... took nearly 6 minutes! I may have to optimize some of my instructions...

### 17:18 MDT

Argh, not sure if I hit another one of the hideous loops or not... will have to step through again.

### 19:00 MDT

Finally found my last self-test bug. My GT wasn't checking for registers, thought I corrected all instances... sigh. Now into the next part. Note to self. An empty string is a valid input, sneaky bastards.

## Tuesday, March 18th, 2014

### 22:30 MDT

Alright no matter what I enter it just loops, input is now being stored into an input buffer I can see it reading into memory. I've found where in the programs memory it's storing the "commands" but they don't match.

In a last stroke of good news I found where it's comparing the users input to the commands length one at a time. Tomorrow I'll type in help and step through to see if I can figure why my input doesn't match what they have in memory.

## Thursday, March 20th, 2014

### 19:12 MDT

Holy crap I'm an idiot... in an effort to save operations in the EQ operation I flip the register to be false to begin with. So if you have something like

```EQ @3, @0, @3```

Guess what? @3 was overwritten before the comparison. Yea, I'm an idiot. I just finished getting the first code from the "game". I've also become the delightful snack to a grue twice, that bastard.

### 21:09 MDT

After dinner with the wife and roommate came back and solved the math problem with a quick little script. Made it to the office and then felt dejected. I hadn't enabled my debuggers spy to keep an eye on where in memory the program was and to make the next section work it's going to require rewriting parts of the app.....

I have some notes on getting through the maze again hopefully I can move through quickly and figure out where in memory we're at when we need to optimize the algorithm. Sneaky giving me an invalid code though... talk about false hope. Oh well, more tomorrow.

## Friday, March 21st, 2014

### 12:00 MDT

The creator of the challenge clarified that the code was, in fact, a bad code. So I had a bug somewhere in my VM. At first I was dismayed, where the hell could I have a bug that would output several correct codes and one failed one... Then as we were chatting it hit me. GT was nearly a copy/paste of EQ. I bet I was clearing the register before comparison. A quick change and off I went. The maze was a little more complicated almost inverted from before (gee I wonder why). But I made it through and got the correct code. Now I'm onto the 7th and 8th.

### 18:00 MDT

OK, I finally, officially solved the maze. Stupidly simple. Just remember 1, 2, 4, 2. If you don't know what that means. Good, go figure out your own solution. The last part is proving to be a pain in the ass. I see the impossibly complex loop. It all starts at ```[05451]``` and drives me insane at ```[06027]```.

## Wednesday, March 26th, 2014

# 18:00 MDT

I haven't worked on this in a while. I attempted to get a curses based debugger going and just got annoyed. I also tried to build a vault solver and I think there is a rule I'm missing... I don't think it's just a star-node problem... For instance I can't return to or enter the starting room or end room more than once. Beyond that I'm going to have to debug the source to figure out what it wants. I'd still like to build some sort of UI for my VM debugger to make things a little easier to visualize as I step through memory. What the current call stack looks like, memory, registers, stack, and memory exporer... perhaps wx? I'll play with that next. I know I don't need it but it would make this part of the puzzle a little easier.

## Saturday, April 12th, 2014

# 11:52 MDT

I had one goal for today, decipher the teleporter validation loop. First task was to capture the loop so I could examine it in it's entirety. To do this I decided to use the teleporter twice in a row. Figuring if I did this then the loop would have to exist between the two IN instructions.

Secondly, to accomplish the first goal I had to modify my debugger to output to a separate buffer. It was difficult to spy on things and get useful output from the program. To do this I made it so the debugger wrote to a file and I just ```tail -f``` the file.

Once I had the loop captured in a file I started sifting through the call stack. I knew that the loop had to exist between two checks of the @7 register. Once I identified those two points I extracted that part out into it's own file (see loop.txt).

Then I started annotating the code, line by line. I've learned a lot in this research.

1. There is a loop which works with the memory addresses 27101 to 27106. However at 27107 there is what appears to be a value which may affect the outcome of the validation loop. I'm not sure yet, but a simple modification at 05655 to be 27102 would test this idea. I didn't do that yet as I wanted to see what else was happening.
2. Further along, at 05667 it looks like some sort of decoding is happening in memory. I've only stepped through about 1/8th of this part of the loop so far but it's doing a lot of memory reading/writing which makes me think it's decoding something.

Based on where I am in the annotation and stepping through I need to make it through roughly 4,453 more steps before I have the full image. I'm hoping I don't have to annotate all the way there just to figure this out though. I think something along the lines will stand out and let me figure out what is happening.

So far my hypothesis's are the following

1. Something is being decoded in memory and checked against for valid decryption...
2. Something is being decoded in memory that will be jumped to.

I'm still not sure which is the valid answer but it's family time. I'll just have to come back later.