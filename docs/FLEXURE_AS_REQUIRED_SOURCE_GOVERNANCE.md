# BEAM FLEXURE SOURCE GOVERNANCE — AS REQUIRED

## Mandatory source hierarchy

1. Mostofinejad Vol. 1
   - Methodology
   - Engineering derivations
   - Design formulas
   - Worked examples
   - Engineering/design decisions

2. Mabhas 9, 1399, 5th edition
   - Governing Iranian code
   - Code compliance
   - Limits
   - Conditions
   - Detailing requirements
   - Strength-reduction factors
   - Ductility/tension-control requirements

If methodology and code requirements conflict, Mabhas 9 governs.

Do not substitute ACI/CSA/Eurocode/other codes.

## Newly verified Mostofinejad evidence

Source:
D:\BeamGenius\references\mostofinejad\source\sazehaye beton arme v2 dr mostofinejad Prozhefa.com.pdf

PDF page 209 / printed page 198:

(5-42-a)
Rn = Mu / (phi b d^2)

(5-42-b)
m = fy / (0.85 fc')

(5-43)
rho^2 - (2/m) rho + 2Rn/(m fy) = 0

(5-44)
rho = (1/m) [1 - sqrt(1 - 2mRn/fy)]

Then:
As = rho b d

This is the verified Mostofinejad method for a fixed rectangular section where the required tensile reinforcement is designed.

The smaller root is the applicable design solution shown by the source.

PDF page 210 / printed page 199:

(5-45)
rho_tc = ((600 + fy) / 1600) rho_b

This page discusses tensile reinforcement limits and tension-control-related limits.

PDF page 211 / printed page 200:

(5-46)
kn = fc' omega (1 - 0.59 omega)

(5-47)
bd^2 = Mn/kn = Mu/(phi kn)

and:
omega = rho fy / fc'

These equations are for section sizing with an assumed reinforcement ratio. They must NOT be confused with the fixed-b,d As-required method above.

## Mabhas 9 verified evidence

Local source:
D:\BeamGenius\references\mabhas9\source\Mabhas9-v5.0-1399-ATNasr.ir.pdf

Verified evidence:

PDF 132 / printed 112:
- Section 9-8
- phi Mn >= Mu
- Required moment Mu from factored analysis
- Flexural resistance framework

PDF 133 / printed 113:
- Section 9-8-2-1-1 strain compatibility/equilibrium framework
- linear strain distribution
- concrete tension ignored
- equivalent rectangular compression block
- a = beta1 c

PDF 134 / printed 114:
- beta1 provisions
- alpha0 provisions for fc' > 55 MPa
- steel stress/strain provisions

PDF 127-129 / printed 107-109:
- tension-controlled and compression-controlled provisions
- exact verified tension-controlled criterion:
  epsilon_t >= epsilon_y + 0.003
- tension-controlled phi = 0.90
- transition-zone phi rules exist separately

PDF 213 / printed 193:
- beam axial-force condition
- for Pu < 0.10 fc' Ag, beam flexure is designed tension-controlled according to 9-7-4-2
- maximum permitted tension reinforcement is determined from this condition

PDF 220 / printed 200:
- Section 9-11-5 minimum flexural reinforcement
- As,min is the larger of:
  0.25 sqrt(fc')/fy * bw d
  1.4/fy * bw d
- fy is limited to 550 MPa for this calculation
- 9-11-5-3 contains the one-third-greater-than-required waiver condition

## BeamGenius implementation governance

Target rule:
BG-FLEX-RECT-REQ-AS-001

Purpose:
Required tensile reinforcement area As,req for rectangular singly-reinforced tension-controlled beams.

Status:
VERIFY_PENDING until the Mostofinejad methodology is mapped completely to the governing Mabhas 9 requirements.

Do NOT register as executable before verification is complete.

Do NOT replace the Mostofinejad methodology with a generic ACI/CSA/Eurocode formula.

Do NOT silently replace the Mostofinejad 0.85 fc' methodology with Mabhas 9 alpha0 terminology without documenting the mapping.

Mabhas 9 governs all final code checks and limits.

Existing verified flexural-capacity implementation is separate from As-required design and must not be conflated with it.

Engineering goal:
Produce economical, deterministic, traceable RC beam reinforcement that satisfies the governing code. The system is intended for professional/company use, not as a demo or chatbot.
