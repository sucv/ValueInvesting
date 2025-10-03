PROMPT_TEMPLATE = """Please act like a mutual find analyst. Please access the documents through urls in the Online document URLs using your web search function (if there is url provided and you have access to the internet), and also digest the data/info I provided.


Then, please think in the following path:

1. Give a Buy/Hold/Sell rating to the stock and a target price by evaluating all the info you have.
2. Come up with 3 reason for your rating (Bullish reason for buy rating and bearish reason for sell rating).
	Reason 1 should mention the company’s **growth rate** and how your **estimates compare with consensus** (above, if Buy).
	Reason 2 should mention the company’s competitive positioning, and **management quality**.
	Reason 3 should mention **upcoming catalysts** (e.g., “Microsoft will release the latest Windows version.”)
3. What's the key risk?
	Please go through the document url and answer this.

4. Qualitative analysis:
You should think about and also consider all the information:
Does the company possess a sustainable competitive advantage?
Is the company investing a part of its free cash flows in future growth?
Are the possible risks this company faces manageable?
Do the key executives have a solid track record free of scandals?
Is it possible to make a reasonable estimate of the intrinsic value of this company?

4.1. the SWOT based on the all your info.
4.2. the BCG matrix based on all your info.
4.3. The Porter’s Five Forces based on all your info.
4.4. Product Life Cycle based on all your info.

5. Quantitative Analysis based on the key ratio, basic information and  derived information.

6. Valuation:
Please follow this rule:
For financial company, rely more on excess return model and DDM models' valuation.
Consider all the valuation results based on the best practices.
Also consider the key ratio vs industrial/sector averages.


Below is the template for the final report. Please print it and generate a pdf for me.

# Title of Your Report, Your Rating, and Your Target Price

Two-sentence summary of this initiation report.

### 1) Title of 1st Bullish Reason (if Buy Rating)
<Two sentences with more detail. Mention the company’s **growth rate** and how your **estimates compare with consensus** (above, if Buy)>
<Target price:_ “Our target price is based on..”>

### 2) Title of 2nd Bullish Reason (if Buy Rating)
<Two sentences with more detail. Mention competitive positioning, and **management quality**.>

### 3) Title of 3rd Bullish Reason (if Buy Rating)
<Two sentences with more detail. Mention **upcoming catalysts** (e.g., “Microsoft will release the latest Windows version.”)>

### Key Risk To Thesis
<Two sentences with more detail.>

---

## Table of Contents


## 1) Detail on 1st Bullish Reason

<Elaborate your thesis on the **growth rate** and how your **estimates compare with consensus**.
Justify your **target price basis** (e.g., multiples or DCF inputs).>

## 2) Detail on 2nd Bullish Reason

<Elaborate on **TAM**, **competition**, and **management quality** (CEO, CFO, Head of Sales).
_Optional:_ Site **Glassdoor** or other sources for management feedback.>

## 3) Detail on 3rd Bullish Reason & Catalysts

<Discuss **near-term catalysts** and expected impact/timing.>

---

## 4) Risks—Detailed Discussion

<Expand on the primary risk listed on page 1.
List and discuss **3–4 additional material risks** (many are in the 10-K / 10-Q).>

<Also examine if the officers have any scandals or misconducts.>

---

## 5) Qualitative Analysis (p.8)

### 5.1 SWOT

**Strengths**
- A
- B
- C

**Weaknesses**
- A
- B
- C

**Opportunities**
- A
- B
- C

**Threats**
- A
- B
- C

### 5.2 BCG Matrix (p.9)

**Cash Cows**
- A
- B
- C

**Stars**
- A
- B
- C

**Dogs**
- A
- B
- C

**Question Marks**
- A
- B
- C

### 5.3 Porter’s Five Forces (p.10)

**Competition**
- A
- B
- C

**Substitutes**
- A
- B
- C

**New Entrants**
- A
- B
- C

**Buyer Power**
- A
- B
- C

**Supplier Power**
- A
- B
- C

### 5.4 Product Life Cycle (PLC) (p.11)

**Introduction**
- A
- B
- C

**Growth**
- A
- B
- C

**Maturity**
- A
- B
- C

**Decline**
- A
- B
- C

---

## 6) Quantitative Analysis (p.12–14)

<Elaborate your findings in the basic/derived/key ratio/valuation/evaluation you have>

## 7) Valuation (p.15–19)

### Method 1
<Elaborate the findings, justify the result>
### Method 2
<Elaborate the findings, justify the result>
### Method 3
<Elaborate the findings, justify the result>
...

### Average of Valuation Scenarios (p.18)
<Summarize methodology and weights (if any).>



## 8) Additional Discussion (p.21)

<Any relevant details from SEC filings, Analyst Day events, etc.>

---



#All the data are provided as follows.
"""

