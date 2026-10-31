# Hindi and Hinglish demonstration coverage

Curated examples of supported phrases, not independent multilingual accuracy. No Hindi/Hinglish sarcasm benchmark. All adapted outputs require review.

Result: 17/18 expected emotion labels; both transformers and embeddings verified for every case.

| Input | Expected | Predicted | Requires review |
|---|---|---|---|
| Main bahut khush hoon | joy | joy | True |
| Main bahut udaas hoon | sadness | sadness | True |
| Mujhe gussa aa raha hai | anger | anger | True |
| Mujhe darr lag raha hai | fear | fear | True |
| Mujhe ghin aa rahi hai | disgust | disgust | True |
| Main hairan hoon | surprise | surprise | True |
| मैं बहुत खुश हूँ | joy | joy | True |
| मैं बहुत उदास हूँ | sadness | sadness | True |
| मुझे गुस्सा आ रहा है | anger | anger | True |
| मुझे डर लग रहा है | fear | fear | True |
| मुझे घिन आ रही है | disgust | disgust | True |
| मैं हैरान हूँ | surprise | surprise | True |
| Main aaj bahut khush hoon because I passed my exam | joy | joy | True |
| Main bahut udaas hoon because my best friend left | sadness | anger | True |
| Mujhe gussa aa raha hai because you broke my phone | anger | anger | True |
| मुझे डर लग रहा है because someone is following me | fear | fear | True |
| मुझे घिन आ रही है from the rotten food | disgust | disgust | True |
| मैं हैरान हूँ to see this unexpected gift | surprise | surprise | True |
