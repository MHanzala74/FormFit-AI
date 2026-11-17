# Exercise definitions

Angles are measured in degrees in 2D image space. "Rest" is the angle where a rep starts/ends; a rep only counts when the
peak reaches `target` (± tolerance 5°). Every issue seen during a rep costs 20 points of that rep's form score.

| Exercise | Primary angle | Start (<) | Rest (>) | Target (≤) | Min rep time |
|---|---|---|---|---|---|
| Squat | knee: hip-knee-ankle | 145 | 160 | 100 | 0.8 s |
| Push-up | elbow: shoulder-elbow-wrist | 140 | 160 | 95 | 0.8 s |
| Lunge | smaller of the two knee angles | 145 | 160 | 100 | 0.8 s |
| Bicep curl | elbow | 130 | 150 | 55 | 1.0 s |

## Form rules

| Exercise | Rule | Threshold | Message |
|---|---|---|---|
| Squat | Torso lean from vertical (shoulder vs hip) while active | > 55° | Keep your chest up |
| Push-up | Shoulder-hip-ankle angle, hips below line | < 155° | Don't let your hips sag |
| Push-up | Shoulder-hip-ankle angle, hips above line | < 155° | Lower your hips |
| Lunge | Torso lean while active | > 25° | Keep your torso upright |
| Curl | Upper-arm drift from vertical while active | > 30° | Keep your elbow by your side |
| Curl | Torso sway from vertical while active | > 20° | Don't swing your body |
| Any | Rep faster than minimum time | see table | Slow down |
| Any | Peak shallower than target | - | Go lower / Lunge deeper / Curl all the way up |

## Plank (timed)

- In position when the shoulder-ankle line is within 35° of horizontal.
- Hold time accumulates while the shoulder-hip-ankle angle is ≥ 160°.
- Voice announcement every 10 s; a hold of at least 3 s is recorded when form breaks (score 80) or the person leaves the
  position (score 100).

## Tuning

Thresholds are class attributes (`rest_angle`, `target_angle`, `MAX_TORSO_LEAN`, ...). Subclass and override them to fit your
mobility, camera height or training goal. These defaults are general-purpose and are not medical or coaching advice.
