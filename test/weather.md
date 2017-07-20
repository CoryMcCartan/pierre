# The Weather

What will the weather be like next week? We can't know for sure, but we can make
a guess.  Bayes' rule will allow us to do this in an intelligent way.

# Hypotheses
The weather can either be sunny, rainy, or cloudy with no rain. On average,
Seattle has `sunnyDays = 165` sunny days, `rainyDays = 152` rainy days, and
`cloudyDays = 365 - sunnyDays - rainyDays [48]` days with clouds but no rain.

Dividing out by 365 days in the year, we have

    @priors
    Sunny: sunnyDays / 365 [0.452055]
    Rainy: rainyDays / 365 [0.416438]
    Cloudy: cloudyDays / 365 [0.131507]

---
# Updates

## Forecast
The forecast for next week says there is a 5% chance of rain.  

    @evidence
    Sunny: 0.8 [0.452055 ==0.8==> 0.899183]
    Cloudy: 0.15 [0.131507 ==0.15==> 0.049046]
    Rainy: 0.05 [0.416438 ==0.05==> 0.051771]
