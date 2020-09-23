## Lets make some pretty good predictions!

Hello!

Here are some data sets with pre-dispatch data combined with the actual price, some weather data, and some derived values like reserve capacity, is it a workday, etc.

This data goes from 2015 onwards.

With one simple command the data will be ready to jam straight into a machine learning algorithm and get some pretty good wholesale price predictions for that Australian National Market!

It doesn't include WA or TAS as capacity and monopoly markets aren't real markets. Also until WA changes the 'WEM' acronym from 'Wholesale Electricity Market' to something more approriate.... oh I don't know like 'WA Electricity Market' it doesn't exist as a state to me.

## How to create the training set

Git apparently hates big data and doesn't let you easily store big files in the repo.

That's fine though, you can see there's a lot of little files in /files.

To stich them all together, open one of the files in excel, then copy that file, remove the first row, open the second file and post the data from the first file into the seco... haha just kidding


- Download python and pip 
- make a virtual environment (optional)
```
pip install requirements.txt

python training_set_creation.py
```
* wait like 20-30 minutes and tada you have some ready to go training sets


## What do all the columns mean?
- **UNIXTIME:** Don't use this column as a feature, it just for reference, and the number of seconds since 1/1/1970.
- **TEMP:** In celcius.
- **HUMIDITY:** % Humdity represented as a decimal from 0 to 1.
- **SPEED:** Wind speed m/s.
- **DIRECTION:** Wind speed direction in degrees.
- **PERIODIDPREDICTED:** The PeriodID of the period it's predicting.
- **CLOUD:** % Cloud represented as a decimal from 0 to 1.
- **RRPACTUAL:** What the price actually was in this period.
- **RRPPREDICTED:** What pre-dispatch said the price would be in this period at the time of prediction (UNIXTIME).
- **TOTALDEMANDPREDICTED:** Demand prediction in MW.
- **AVAILABLEGENERATIONPREDICTED:** Available generation prediction in MW.
- **NETINTERCHANGEPREDICTED:** Net interconnector flows of the region.
- **HORIZON:** Number of periods the actual period is away (0 means this period starting now, 1 mean 1 more period to go).
- **WORKDAY:** 1 if workday, 0 if weekend or between 24/12 and 1/1.
- **MONTH:** From 1-12.
- **CAPACITYRESERVE:** Does this look right:
  
   ('AVAILABLEGENERATIONPREDICTED' - 'TOTALDEMANDPREDICTED' - 'NETINTERCHANGEPREDICTED')/'AVAILABLEGENERATIONPREDICTED'
   
   I hope it's right. Capapacity Reserve % as a decimal from 0 to 1.

You can see how some of these derived values are calculated in `training_set_creation.py`

## Ok I have a training set now what do I do?

If you don't know ML either learn some ML or just throw these CSVs at something like [GCP AutoML Tables](https://cloud.google.com/automl-tables) and let it do the work. More features is not always better, I've found just using these features it pretty effective:
- TEMP
- SPEED
- PERIODIDPREDICTED
- RRPPREDICTED
- TOTALDEMANDPREDICTED
- AVAILABLEGENERATIONPREDICTED
- NETINTERCHANGEPREDICTED
- WORKDAY
- MONTH
- CAPACITYRESERVE

Obviously your target column is RRPACTUAL. Do not use RRPACTUAL as a feature column.

Probably optimise for RMSE. You want to be predicting outliers (i.e. high prices) so don't use a technique that ignores outlier results.

## These output predictions are pretty good, but sometimes they're weird.

Yeah, AI doesn't naturally pick up the huge amount of ways that the NEM markets get distorted by the humans, so you're going to need some post processing.

You'll probably see when there's a high price the predictions fall within $500-$2000. Shifting and stretching than band above $1000 and out to... a number higher than $2000 is pretty effective. It's pretty safe to assume it's unlikely a price will fall between $300-$1000, and most models are a little gun-shy on those higher prices.

## How do I make these better?

First, decide on what better means. If you're just trying to predict the price accurately, Mean Average Error is a pretty good KPI. If you're doing something like Demand Response and want to know if the price will be over/under $1000/MW, then use False Positive/Negative on Price >$1000 as your KPI.

One thing that's cool is if there is headroom on the interconnectors, the prices between those states tend to be similar, and if the internconnector is a max then the prices are likely to diverge. This means that for regions that are predicted to have interconnector headroom, you can average those prices together and now you can say your model uses an "ensemble method".

E.g. lets say the price predictions are QLD:$200, NSW:$100, VIC:$120, SA: $120 and the only interconnector constraint is at QLD-NSW, it's probably reasonable to make the prices QLD:$200, NSW:$113.3, VIC:$113.3, SA: $113.3

Try some other statical techniques too, especially if they have cool names like "random forrest" and "sparse regression lasso".

If you are wanting to predict something like "Will the price be over $1000?" then you can change your RRPACTUAL column from the actual price, to a 1 if the price was over $1000, or 0 if the price was under $1000. This model will now predict a value between 0 and 1, which is roughly the proability of exceeding $1000. This, combined with the actual price prediction now gives you both the expected value, and describes the distribution of the possible values in a way that might be useful for you.

## Where can I get weather data
Lots of places, I like:
Current Weather + Forecasts: [Willy Weather](https://www.willyweather.com.au/info/api.html) although it doesn't include cloud cover forecasts
Historical: [Open Weather Map Bulk History](https://openweathermap.org/history-bulk) Flat fee of $10/location and goes back to 1979! Way before electricity was even invented.

## Your advice is dumb and my advice is better

Please submit a pull request and let us all know how we can predict energy prices better!

Also if anyone has anything that would be useful for this repo: scripts, files, improvements to this README then please feel free to submit a pull request, or just fork it and take all the credit. And please do the same for any errors I have included.




