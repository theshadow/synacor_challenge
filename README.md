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