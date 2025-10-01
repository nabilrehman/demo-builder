import { Loader2 } from "lucide-react";
import { useState, useEffect } from "react";

const WITTY_MESSAGES = [
  "Performing a LEFT JOIN... because no data should feel left out.",
  "Feature engineering... getting the data ready for its big job interview.",
  "Running anomaly detection... and finding the one data point that didn't laugh at the joke.",
  "Applying a validation schema... this is the bouncer, and your data's name isn't on the list.",
  "Querying cold storage... waking the data up from hibernation. It's a bit grumpy.",
  "Checking for data provenance... trying to find out who raised this dataset.",
  "Performing A/B testing... trying to decide which version of reality is less buggy.",
  "Building the data dictionary... because this data has its own confusing dialect.",
  "Handling streaming data... just trying to take a sip from a firehose.",
  "Enforcing data governance... because this data has a history of making bad decisions.",
  "Joining tables... playing matchmaker for lonely datasets.",
  "Vectorizing your words... because math is so much easier to deal with than feelings.",
  "Aggregating results... I'll give you the short version of the story.",
  "Reducing dimensionality... this problem was giving me a headache, so I'm simplifying it.",
  "Parsing log files... reading the server's diary to see what it's really thinking.",
  "Asking the dataset to check its privilege... mitigating sampling bias.",
  "Data imputation in progress... making an educated guess, with a heavy emphasis on 'guess'.",
  "Clustering the data points... helping the data find its friend group.",
  "The ETL pipeline is clogged... we may need to call a data plumber.",
  "Serializing the data... packing it a lunch for its trip across the network.",
  "Masking PII... giving your data a secret identity and a cool disguise.",
  "Profiling the data... trying to understand its hopes, its dreams, its deepest fears.",
  "Handling outliers... gently escorting the weird data points to the exit.",
  "This unstructured data looks like my laundry pile... beginning classification.",
  "Reverse ETL-ing... it's like putting the clean, folded laundry back on the messy floor.",
  "The data is undergoing a transformation... it's having its ✨glow-up✨ moment.",
  "Building an index... writing the table of contents after the book is already finished.",
  "ACID compliance check... making sure the database's promises are legally binding.",
  "Sharding the database... this dataset got too popular for one server.",
  "Reshaping the dataframe... the data is hitting the gym to get into shape.",
  "Running a query with a HAVING clause... because the data is being a little picky.",
  "Managing the data lifecycle... planning for this data's eventual retirement.",
  "Sampling the dataset... because ain't nobody got time to read the whole thing.",
  "Moving data to cold storage... putting the old files in the attic. Hope I remember they're there.",
  "Checking for multicollinearity... making sure the features aren't just telling me the same thing in different fonts.",
  "Trying to read this corrupted file... it's like deciphering a doctor's handwriting.",
  "This data silo won't share... currently negotiating a data custody agreement.",
  "Geocoding addresses... finding out where all this data lives. Don't worry, I won't show up unannounced.",
  "This data is right-skewed and a little bit sassy... attempting normalization.",
  "Searching the metadata... it's like looking for the 'Nutrition Facts' on a data package.",
  "Compressing data... trying to fit ten pounds of information into a five-pound bag.",
  "Handling missing values... trying to fill in the awkward silences in the dataset.",
  "This real-time analysis is like trying to have a conversation with someone who keeps interrupting.",
  "Data cleansing... I've seen cleaner data in a toddler's art project.",
  "The query is returning too many results... I'm going to need a bigger LIMIT.",
  "Casting data types... because the data showed up in the wrong outfit for the party.",
  "Following the data lineage... walking the breadcrumbs back to see who made this mess.",
  "Partitioning the table... this family dinner is getting too big, so we're setting up a kids' table.",
  "That's not an anomaly... it's just a data point with a strong personality.",
  "Querying the graph database... now we get to see who is friends with whom.",
  "Validating the results... because this data has a tendency to exaggerate.",
  "Scrubbing the data... found something sticky in column H.",
  "Trimming whitespace... for a leaner, meaner dataset.",
  "Standardizing date formats... because everyone has their own concept of time.",
  "Wrestling with a deeply nested JSON object. Send coffee.",
  "Herding stray data points back into the cluster.",
  "Asking the data for its opinion. It's biased.",
  "This dataset is 99% clean. It's the 1% that will get you.",
  "Checking data integrity... trust, but verify.",
  "This data tells a story, and I'm the interpreter.",
  "Taming the data firehose. It's a bit spicy today.",
  "Anonymizing PII... your secrets are safe with me.",
  "Fighting with character encodings... why is there a snowman emoji in the address field?",
  "Navigating the data warehouse... aisle 7 has the good stuff.",
  "The data is not wrong, it's just... creatively sourced.",
  "Letting the data speak for itself... but it's mumbling.",
  "Fact-checking the data... and the data's sources.",
  "Filling in the null values... and the void in my heart.",
  "Dealing with errant commas in the CSV... the agents of chaos.",
  "This data has more issues than my last relationship.",
  "Converting to Parquet... for that columnar goodness.",
  "Juggling the three V's... Volume, Velocity, and a Very large headache.",
  "Plotting the data points... and my eventual escape.",
  "Looking for the signal in the noise... it's very faint.",
  "Checking the GDPR rulebook... just to be sure.",
  "This data has been denormalized for your viewing pleasure.",
  "Reshaping the dataframe... it's hitting the gym.",
  "The data appears to be right-skewed and a little bit sassy.",
  "Casting data types... int to string is easy, regret to acceptance is harder.",
  "I've seen cleaner data in a toddler's lunchbox.",
  "Rehydrating the data lake... it was getting a bit dry.",
  "Polishing the data until it shines.",
  "Our engineers are aware of the situation and are currently crying.",
  "Generating a plausible excuse for this delay...",
  "Patience is a virtue. I am currently testing yours.",
  "Assembling the IKEA furniture that is your request.",
  "The progress bar is a lie, but a comforting one.",
  "This is taking longer than the meeting that could have been an email.",
  "Waking up the intern who runs this script.",
  "Letting the bits cool down.",
  "So long, and thanks for all the data.",
  "Are you sure you want to rm -rf /? Thinking about it...",
  "It worked on my machine.",
  "Searching for a suitable emoji... 🤔",
  "Parsing the syntax tree... this is more complicated than my family tree.",
  "ETL complete. The data is now ✨ a different kind of messed up ✨.",
  "This database is held together with duct tape and a single SELECT *.",
  "The primary key is sacred. Do not question the primary key.",
  "Waiting for the cron job to finish... any decade now.",
  "Normalizing the schema... because this data is just not normal.",
  "Committing transaction... no turning back now.",
  "Writing a complex query... brb, grabbing my wall of strings and pushpins.",
  "Running a regression... on my life choices.",
  "Avoiding data leakage... by putting a bucket under the server.",
  "Analyzing sentiment... and my own feelings about this data.",
  "Extracting key topics... one awkward pause at a time.",
  "Transcribing audio... please speak clearly, unlike my last relationship.",
  "Wrangling unstructured data... it's like herding cats, but with more semicolons.",
  "Polishing the data lake... trying to get a clear reflection.",
  "Building the data pipeline... hope there are no leaks.",
  "ETL-ing... (Extracting, Transforming, Loading... and lots of coffee).",
  "De-duping records... I've had this conversation before...",
  "Searching for insights in the noise...",
  "Normalizing the dataset... because 'weird' is hard to quantify.",
  "Gauging the emotional temperature... it's getting spicy.",
  "Identifying speakers... and assigning blame.",
  "Scrubbing PII... your secrets are safe with me.",
  "One moment, running a regression on your conversation..."
];

const getRandomMessage = () => {
  return WITTY_MESSAGES[Math.floor(Math.random() * WITTY_MESSAGES.length)];
};

export const LoadingState = () => {
  const [currentMessage, setCurrentMessage] = useState(getRandomMessage());

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentMessage(getRandomMessage());
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-3 text-muted-foreground animate-fade-in">
      <Loader2 className="h-4 w-4 animate-spin" />
      <span className="text-sm">{currentMessage}</span>
    </div>
  );
};
