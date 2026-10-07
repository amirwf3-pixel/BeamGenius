# FLEXURAL AS-REQUIRED — MOSTOFINEJAD TO MABHAS 9 MAPPING

## Status

VERIFY_PENDING

Target rule:
BG-FLEX-RECT-REQ-AS-001

No executable implementation is authorized by this document alone.

## 1. Methodology source

Mostofinejad Vol. 1 is the engineering/methodology source.

For a rectangular section with fixed b and d, Mostofinejad relation (5-44) gives:

Rn = Mu / (phi b d^2)

m = fy / (0.85 fc')

rho = (1/m) [1 - sqrt(1 - 2 m Rn / fy)]

As = rho b d

Source:
Mostofinejad PDF page 209 / printed page 198.

The smaller quadratic root is the selected design solution.

## 2. Governing code source

Mabhas 9 is the governing source for code compliance.

Verified Mabhas 9 flexural framework:

phi Mn >= Mu

a = beta1 c

Concrete equivalent compression block:
normal case: 0.85 fc'

High-strength provision:
alpha0 fc' where applicable according to Mabhas 9.

Tension-controlled condition:

epsilon_t >= epsilon_y + 0.003

For tension-controlled sections:

phi = 0.90

## 3. Engineering mapping

Mostofinejad's 5-44 is a methodology for solving the required tensile reinforcement ratio for a fixed rectangular section.

It must not be copied blindly into BeamGenius as a code formula.

The engineering structure is:

1. Start from factored Mu.
2. Use the governing rectangular-section compression block.
3. Establish force equilibrium between tensile reinforcement and concrete compression.
4. Establish nominal flexural resistance.
5. Apply the governing phi factor.
6. Solve for the smaller physically meaningful tensile-steel root.
7. Convert rho to As.
8. Apply Mabhas 9 minimum reinforcement.
9. Apply Mabhas 9 tension-control / maximum reinforcement limits.
10. Verify final provided reinforcement independently.

## 4. Important parameter mapping

Mostofinejad fixed-section equation uses:

0.85 fc'

Mabhas 9 must govern the actual concrete compression stress block.

Therefore BeamGenius must not hard-code the Mostofinejad 0.85 coefficient as the governing code coefficient for all concrete strengths.

The mapping between:

Mostofinejad:
m = fy / (0.85 fc')

and Mabhas 9:
concrete compression block based on beta1 and the governing compression stress intensity

must be explicitly implemented/documented.

For normal-strength concrete, the Mabhas 9 verified source gives the 0.85 fc' block.

For fc' above the applicable Mabhas 9 threshold, the alpha0 provision must govern.

## 5. beta1

Mabhas 9 verified source provides beta1 as part of the equivalent rectangular compression block.

Therefore beta1 is a governing code parameter in the BeamGenius implementation.

It must not be imported from Mostofinejad when the Mabhas 9 requirement differs.

## 6. phi

Mostofinejad methodology may use phi as an input/design factor.

BeamGenius shall determine phi according to Mabhas 9.

For the current target scope of tension-controlled beams:

phi = 0.90

with:

epsilon_t >= epsilon_y + 0.003

Transition-zone behavior is outside this target rule unless explicitly added as a separate verified rule.

## 7. Minimum reinforcement

After calculating the required flexural reinforcement, Mabhas 9 minimum reinforcement must be checked.

As,min is the larger of:

0.25 sqrt(fc') / fy * bw d

1.4 / fy * bw d

The Mabhas 9 fy limitation for this calculation must be respected.

The final required design reinforcement must account for the governing minimum requirement.

## 8. Maximum reinforcement / ductility

The target rule is restricted to tension-controlled singly reinforced rectangular beams.

The final design must satisfy:

epsilon_t >= epsilon_y + 0.003

The maximum permitted tensile reinforcement must therefore be derived/checked from the Mabhas 9 tension-control boundary.

Existing BeamGenius capacity evaluation already contains a tension-control check. The new As-required rule must remain logically separate from capacity evaluation.

## 9. Not allowed

Do not:

- replace Mabhas 9 with ACI/CSA/Eurocode;
- treat Mostofinejad's 0.85 coefficient as universally governing;
- use the 0.59 coefficient from relation (5-46) for fixed-section As-required design;
- confuse section-sizing relations (5-46)/(5-47) with relation (5-44);
- silently reuse unverified code constants;
- register BG-FLEX-RECT-REQ-AS-001 as executable while any governing mapping remains VERIFY_PENDING.

## 10. Current unresolved items

1. Exact algebraic mapping of relation (5-44) to the Mabhas 9 stress-block parameters.
2. Exact applicability of alpha0 versus 0.85 fc' across the supported fc' range.
3. Exact As,max expression from the Mabhas 9 tension-controlled boundary.
4. Interaction between calculated As, required As,min, and the 9-11-5-3 one-third waiver.
5. Exact input/scope restrictions for this first executable As-required rule.

Until these items are verified, BG-FLEX-RECT-REQ-AS-001 remains VERIFY_PENDING.
