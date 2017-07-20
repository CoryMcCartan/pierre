# Where are my keys?

I've lost my keys. I last used them yesterday, when I drove back from work. I 
usually put them on a hook by the door, but they aren't there. They could be in
the junk drawer, the car, the kitchen, my clothes, or somewhere else. Since they
weren't on the hook, they're probably in the car.

    @priors
    Car: 5 [0.526316]
    Drawer: 1 [0.105263]
    Kitchen: 1 [0.105263]
    Clothes: 2 [0.210526]
    Elsewhere: 0.5 [0.052632]

I look in the car first since it seems most likely that I'll find my keys there.
But the keys aren't in the car. I think. If they were there, there's a
`carFindProb = 75`% chance I'd find them (there are a lot of nooks and crannies
in a car). So there's a `100-carFindProb [25]`% chance that I missed them. If the
keys are actually elsewhere, then of course I wouldn't find them in the car.

    @evidence: not found in car
    Car: 100 - carFindProb  [0.526316 ==0.058824==> 0.217391]
    Drawer: 100  [0.105263 ==0.235294==> 0.173913]
    Kitchen: 100  [0.105263 ==0.235294==> 0.173913]
    Clothes: 100  [0.210526 ==0.235294==> 0.347826]
    Elsewhere: 100  [0.052632 ==0.235294==> 0.086957]

So next I look in my clothes. Still no keys.  I'm quite sure I'd find the keys if
they were actually there. There's maybe a `clothesMissProb = 2`% chance I'd miss
them. 

    @evidence: not found in clothes
    Car: 100  [0.217391 ==0.248756==> 0.329815]
    Drawer: 100  [0.173913 ==0.248756==> 0.263852]
    Kitchen: 100  [0.173913 ==0.248756==> 0.263852]
    Clothes: clothesMissProb  [0.347826 ==0.004975==> 0.010554]
    Elsewhere: 100  [0.086957 ==0.248756==> 0.131926]

Back to the car. Even though I've already looked there, its prior probability
was higher, and I didn't do a super-thorough search the first time. Now I'll
really go over it with a fine-tooth comb. There's only a `carMissProb2 = 5`%
chance I've missed my keys now. But they're still not there.

    @evidence: not found in car again
    Car: carMissProb2  [0.329815 ==0.012346==> 0.024015]
    Drawer: 100  [0.263852 ==0.246914==> 0.384246]
    Kitchen: 100  [0.263852 ==0.246914==> 0.384246]
    Clothes: 100  [0.010554 ==0.246914==> 0.015370]
    Elsewhere: 100  [0.131926 ==0.246914==> 0.192123]

On to the kitchen or the junk drawer.  The kitchen is easier, so I'll start
there.  I do a quick scan of the surfaces and don't see the keys. But I'd only
expect to see them maybe 1 in every `kitchenFreq = 3` times 
(`100 / kitchenFreq`% of the time) I do this kind of cursory check.

    @evidence: not seen in kitchen
    Car: 100  [0.024015 ==0.230769==> 0.032286]
    Drawer: 100  [0.384246 ==0.230769==> 0.516573]
    Kitchen: 100 / kitchenFreq  [0.384246 ==0.076923==> 0.172191]
    Clothes: 100  [0.015370 ==0.230769==> 0.020663]
    Elsewhere: 100  [0.192123 ==0.230769==> 0.258287]

I guess now I'll finally check the drawer. No keys! It's a complete mess, so
I'm only `drawerFindProb = 40`% sure I haven't missed them.

    @evidence: not found in drawer
    Car: 100  [0.032286 ==0.217391==> 0.040695]
    Drawer: 100 - drawerFindProb  [0.516573 ==0.130435==> 0.390667]
    Kitchen: 100  [0.172191 ==0.217391==> 0.217037]
    Clothes: 100  [0.020663 ==0.217391==> 0.026044]
    Elsewhere: 100  [0.258287 ==0.217391==> 0.325556]

What? The drawer again? A much more thorough search finally turns up the keys.

    @evidence: found in drawer
    Car: 0  [0.040695 ==0.000000==> 0.000000]
    Drawer: 1  [0.390667 ==1.000000==> 1.000000]
    Kitchen: 0  [0.217037 ==0.000000==> 0.000000]
    Clothes: 0  [0.026044 ==0.000000==> 0.000000]
    Elsewhere: 0  [0.325556 ==0.000000==> 0.000000]

