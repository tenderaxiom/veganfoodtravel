"""Travel planning guides. Each guide: slug, title (SEO), h1, description, lead, sections (h2, html), faqs.
Keep every claim general and checkable: no airline rankings, no prices, no named restaurants."""

GUIDES = [
    {
        "slug": "how-to-ask-for-vegan-food",
        "title": "How to Ask for Vegan Food in Any Country: 3 Questions That Work",
        "h1": "How to ask for vegan food in any country",
        "description": "The three questions I use to eat vegan anywhere, the hidden ingredients to ask about, and the word for vegan in 14 languages.",
        "lead": "Ordering vegan abroad isn't about finding a vegan restaurant. It's about knowing which local dishes are already vegan, where animal products hide, and how to ask for one small change.",
        "sections": [
            ("Question 1: What is already vegan here?",
             "<p>Most food cultures have dishes that never had meat in them. Start there and you'll eat the same food as everyone else, not a sad plate of side dishes.</p>"
             "<ul><li><b>Religious fasting food.</b> Greek Orthodox <i>nistisimo</i> food and Japanese Buddhist <i>shōjin ryōri</i> were plant-based long before anyone said 'vegan'.</li>"
             "<li><b>Peasant cooking.</b> Bean soups, chickpea flatbreads, tomato pasta, vegetable stews in olive oil.</li>"
             "<li><b>Street snacks.</b> Roasted corn and chestnuts, fruit with chilli and lime, chickpea fritters.</li></ul>"
             "<p>Every <a href=\"/#countries\">country guide</a> starts with a list of these dishes.</p>"),
            ("Question 2: What's in the stock or the fat?",
             "<p>The obvious ingredients are easy to spot. The hidden ones are what catch vegans out:</p>"
             "<ul><li><b>Stock:</b> meat or chicken stock in soups, rice and stews; fish stock (dashi) in Japan.</li>"
             "<li><b>Fat:</b> butter on vegetables in France, lard in Mexican beans, duck fat in south-west France, beef dripping in some British chip shops.</li>"
             "<li><b>Sauces:</b> fish sauce in South-East Asia, anchovy in Caesar dressing and some Italian dishes.</li>"
             "<li><b>Finishing touches:</b> cheese grated on top, ham sprinkled over Spanish soups, bonito flakes on Japanese tofu.</li></ul>"
             "<p>Ask about the stock and the cooking fat specifically. 'Is it vegetarian?' won't get you this answer.</p>"),
            ("Question 3: Can they leave one thing off?",
             "<p>Asking for a whole new dish puts a busy kitchen on the spot. Asking to leave one thing off usually works: no cheese on the pizza, no feta on the salad, no egg on the pisto, no cream on the tacos.</p>"
             "<p>Pick dishes that are one change away from vegan. The country guides mark these as <b>Ask for it vegan</b>.</p>"),
            ("Say 'vegan', then spell it out",
             "<p>In many countries 'vegetarian' still means cheese and eggs, and 'vegan' isn't always understood. Say the word, then list what you don't eat: meat, fish, eggs, milk, butter, cheese and honey. A <a href=\"/phrase-cards/\">phrase card</a> in the local language does this in one sentence.</p>"
             "<div class=\"wordtable\">{WORDS}</div>"),
            ("When you're still not sure",
             "<ul><li>Choose dishes that are vegan by tradition over ones that need changing.</li>"
             "<li>Eat where the locals eat that dish every day; they'll know what's in it.</li>"
             "<li>Look for the local word for 'vegan' or for fasting food on menus and labels.</li>"
             "<li>If you have an allergy, treat any answer as a guide, not a guarantee.</li></ul>"),
        ],
        "faqs": [
            ("What's the difference between vegetarian and vegan on a menu?", "Vegetarian dishes usually still contain eggs, milk, butter or cheese. Vegan means no animal products at all. In many countries the word vegetarian is far more common, so always check."),
            ("Do I need to speak the language?", "No. A short written card in the local language, shown to your server, works better than trying to explain out loud."),
            ("Which ingredients are most often hidden?", "Meat or fish stock, butter, lard, fish sauce, and cheese or ham added as a garnish."),
        ],
    },
    {
        "slug": "vegan-meals-on-flights",
        "title": "How to Get a Vegan Meal on a Flight: The VGML Code and What to Pack",
        "h1": "How to get a vegan meal on a flight",
        "description": "How to order a vegan meal on a plane (meal code VGML), when to book it, how to make sure it turns up, and what to pack in case it doesn't.",
        "lead": "Most full-service airlines will load a vegan meal for you if you ask in time. The trick is knowing the code, ordering early enough, and having a back-up in your bag.",
        "sections": [
            ("Order the VGML meal",
             "<p>Airlines use four-letter codes for special meals. The vegan one is usually <b>VGML</b>, often listed as 'Vegetarian (vegan) meal' or 'Vegan meal'. Don't confuse it with:</p>"
             "<ul><li><b>VLML</b> – vegetarian, may include milk, butter, cheese and egg.</li>"
             "<li><b>AVML</b> – Asian vegetarian, often Indian-style; may include dairy.</li>"
             "<li><b>HNML</b> – Hindu meal, meat-free but may include dairy.</li></ul>"
             "<p>Each airline writes its own description, so read it before you choose.</p>"),
            ("When and how to book it",
             "<ul><li>Add the meal when you book, or in 'Manage booking' on the airline's website or app.</li>"
             "<li>Many airlines need the request at least 24 hours before departure, and some need longer. Order as early as you can.</li>"
             "<li>Request it for <b>every flight</b> in your journey, including connections on partner airlines.</li>"
             "<li>If you change flights, check that the meal moved with you. It often doesn't.</li>"
             "<li>If you booked through a travel agent or booking site, check the airline's own website too.</li></ul>"),
            ("Make sure it turns up",
             "<ul><li>Check the booking a day or two before you fly; special meals sometimes drop off after changes.</li>"
             "<li>Tell the crew when you board that you ordered a vegan meal.</li>"
             "<li>Special meals are usually served first, so don't worry if you get yours before everyone else.</li>"
             "<li>Check the bread roll and dessert: sometimes standard items are added to the tray.</li></ul>"),
            ("Low-cost and short flights",
             "<p>Many low-cost airlines and short flights don't offer pre-ordered special meals at all. You buy from a trolley menu, which may have a vegan snack or none. Check the airline's food menu before you fly, and bring your own.</p>"),
            ("What to pack, just in case",
             "<ul><li>Something filling: a sandwich, a wrap, cooked grains or a salad in a sealed box.</li>"
             "<li>Snacks that travel well: nuts, dried fruit, oat bars, rice crackers.</li>"
             "<li>Solid food is fine through security; check the rules for liquids, spreads and hummus.</li>"
             "<li>Eat or bin fresh food before you land. Many countries, including New Zealand and Australia, have strict biosecurity rules and you must declare food on arrival.</li></ul>"),
            ("Eating at the airport",
             "<p>Big airports usually have a few vegan options: falafel, sushi rolls, grain bowls, fruit and plain bread. Smaller airports may have very little, especially late at night, so eat before you leave or bring food.</p>"),
        ],
        "faqs": [
            ("What is the vegan meal code on airlines?", "VGML. It's usually described as a vegan or 'vegetarian (vegan)' meal. VLML is vegetarian and may include dairy and eggs."),
            ("How far in advance should I order a vegan meal?", "As early as possible. Many airlines need at least 24 hours before departure, and some need longer."),
            ("Do budget airlines have vegan meals?", "Some have a vegan snack on the menu, many don't, and most don't take pre-orders. Bring your own food."),
        ],
    },
    {
        "slug": "vegan-friendly-accommodation",
        "title": "How to Find Vegan-Friendly Accommodation: What to Check Before You Book",
        "h1": "How to find vegan-friendly accommodation",
        "description": "What to look for in a hotel, apartment or guesthouse when you're vegan: kitchens, breakfast, location, and the question to send before you book.",
        "lead": "Where you sleep decides how easily you eat. A kitchen, a market nearby and a host who understands 'vegan' make a trip easier than any restaurant list.",
        "sections": [
            ("A kitchen is the biggest win",
             "<p>Apartments, guesthouses and hostels with a kitchen let you cook breakfast, pack lunches and try local produce. Even a fridge and a kettle help. Use the 'kitchen' or 'kitchenette' filter on booking sites.</p>"),
            ("Check the breakfast",
             "<p>Hotel breakfasts are often bread, butter, eggs, yoghurt and cured meat. Before you pay extra for breakfast, ask what's vegan. Fruit, bread, jam, oats and plant milk are a good sign. If the answer is vague, book without breakfast and find a bakery or market nearby.</p>"),
            ("Choose the location for food",
             "<ul><li>Stay within walking distance of a market, a supermarket, or a neighbourhood with lots of restaurants.</li>"
             "<li>Busy areas with Indian, Middle Eastern, Chinese or Ethiopian restaurants nearly always have vegan options.</li>"
             "<li>Before you book, open a restaurant map such as HappyCow or Google Maps and look at what's near the address.</li></ul>"),
            ("Read the reviews for food",
             "<p>Search the reviews for 'vegan', 'vegetarian' and 'breakfast'. Other vegans will usually tell you whether the host made an effort.</p>"),
            ("Send one question before you book",
             "<blockquote class=\"script\">\"I'm vegan, so I don't eat meat, fish, eggs, dairy or honey. Is there anything vegan at breakfast, or can I use a kitchen or fridge?\"</blockquote>"
             "<p>How quickly and how helpfully they answer tells you most of what you need to know.</p>"),
            ("Retreats, farm stays and long stays",
             "<p>Farm stays and small guesthouses will often cook for you if you tell them in advance. For longer stays, a monthly apartment near a market is usually cheaper and easier than eating out every meal.</p>"),
        ],
        "faqs": [
            ("Are hotel breakfasts vegan?", "Usually only partly. Expect fruit, bread and jam; ask about plant milk and anything hot. If it's unclear, book without breakfast."),
            ("What's the best type of accommodation for vegans?", "Anywhere with a kitchen or at least a fridge, close to a market or supermarket."),
        ],
    },
    {
        "slug": "vegan-travel-packing-list",
        "title": "Vegan Travel Packing List: Food, Toiletries and Kit for Eating Well Anywhere",
        "h1": "Vegan travel packing list",
        "description": "What to pack for a vegan trip: travel snacks, kitchen kit, vegan toiletries, and the biosecurity rules to know before you fly.",
        "lead": "You don't need to pack much to eat well as a vegan abroad. A few snacks, one or two pieces of kit, and your phrase cards cover most problems.",
        "sections": [
            ("Food for the journey",
             "<ul><li>Nuts, seeds and trail mix</li><li>Dried fruit and oat or nut bars</li><li>Rice cakes or crackers</li><li>Nut butter in a small jar or sachets (check liquid rules for hand luggage)</li><li>A filling meal for the flight: a sandwich, wrap or grain salad in a sealed box</li></ul>"),
            ("Small kit that makes a big difference",
             "<ul><li>A reusable box and fork or spork for markets and leftovers</li><li>A small knife for fruit and bread (in checked luggage only)</li><li>A reusable water bottle</li><li>A foldable shopping bag for markets</li></ul>"),
            ("Your phrase cards",
             "<p>Save the <a href=\"/phrase-cards/\">phrase card</a> for each country to your phone, and screenshot it in case you have no signal. The <a href=\"/free-guide/\">free PDF pack</a> has all 10 countries in one file.</p>"),
            ("Vegan toiletries",
             "<p>Hotel toiletries are rarely labelled. If it matters to you, bring travel-size vegan shampoo, soap, sunscreen and toothpaste, or solid bars that don't count as liquids.</p>"),
            ("Know the food rules at the border",
             "<p>Many countries restrict food you can bring in. New Zealand and Australia are among the strictest: you must declare all food when you arrive, and fresh fruit and vegetables are usually not allowed. Finish or bin fresh food before you land, and keep packaged snacks sealed and labelled.</p>"),
            ("What not to bother packing",
             "<p>Big bags of food from home. In most countries supermarkets sell bread, beans, nuts, fruit and plant milk, and the local food is the point of going.</p>"),
        ],
        "faqs": [
            ("Can I bring vegan snacks through airport security?", "Solid foods are generally fine. Spreads, hummus and drinks count as liquids in hand luggage in many countries."),
            ("Can I take food into New Zealand or Australia?", "Some packaged food is allowed, but you must declare all food on arrival. Fresh fruit and vegetables are usually not allowed."),
        ],
    },
]
