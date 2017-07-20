#Drug Testing

*(Copied from Wikipedia)*

Suppose a drug test is `sensitivity=99`% sensitive and `specificity=99`%
specific. That is, the test will produce `sensitivity [99]`% true positive results
for drug users and `specificity [99]`% true negative results for non-drug users.
Suppose that `prevalence=0.5`% of people are users of the drug. 

    @priors
    user: prevalence [0.005000]
    non-user: 100 - prevalence [0.995000]

Now suppose Bob tests postivie for the drug. What is the probability that he is
actually a user? 

    @evidence
    user: sensitivity [0.005000 ==0.990000==> 0.332215]
    non-user: 100 - specificity [0.995000 ==0.010000==> 0.667785]

