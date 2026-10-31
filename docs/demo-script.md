# Demonstration script

Presenter: Divyansh Yadav

1. Start the application and wait for model readiness messages.
2. Show /health and identify transformer and retrieval backends.
3. Analyze "I am happy and excited" and inspect scores and warnings.
4. Analyze "Oh great, another delayed train" and explain approximate sarcasm.
5. Try "This is my favorite song" and explain the sincere-praise regression check.
6. Upload a CSV with valid and invalid rows, showing explicit row errors.
7. Open /inspect, compare a saved result and download CSV.
8. Present the measured evaluation table, with the measured warm latency and startup reported separately.

Do not promise fixed prediction percentages or claim that every sarcastic input is recognized. Model behavior and latency vary. The LLM is disabled by default; generated explanations use templates unless a valid provider is explicitly configured.

Show `Main bahut khush hoon` as a limited Hinglish example and explain its review warning. Explain the English temperature-scaled confidence method and that it does not guarantee a correct label.
