from sqlalchemy import text
import asyncio
from app.database import AsyncSessionLocal
from app.models import Activity


# Define your activity data (red_flag, id, step, desc, minutes, materials)
activities_data = [
    # ---- Cannot suck/swallow ----
    ("Cannot suck/ swallow", "cannot_suc_1", 1, "Gently massage baby's cheeks and lips before feeding to stimulate oral muscles", 5, "Minimal everyday household items"),
    ("Cannot suck/ swallow", "cannot_suc_2", 2, "Practice sucking using a clean finger dipped in milk", 10, "Minimal everyday household items"),
    ("Cannot suck/ swallow", "cannot_suc_3", 3, "Offer a slow-flow nipple bottle for practice", 15, "Minimal everyday household items"),


    # ---- Limbs stiff or limp ----
    ("Limbs stiff or limp", "limbs_stif_1", 1, "Do gentle bicycle movements with legs during play", 5, "Minimal everyday household items"),
    ("Limbs stiff or limp", "limbs_stif_2", 2, "Encourage tummy time with support", 10, "Minimal everyday household items"),
    ("Limbs stiff or limp", "limbs_stif_3", 3, "Assist baby in rolling side-to-side with soft stretches", 15, "Minimal everyday household items"),

    # ---- Not looking at mother's face ----
    ("Not looking at mother's face", "not_lookin_1", 1, "Play peek-a-boo at eye level", 5, "Minimal everyday household items"),
    ("Not looking at mother's face", "not_lookin_2", 2, "Hold baby close while feeding and exaggerate facial expressions", 10, "Minimal everyday household items"),
    ("Not looking at mother's face", "not_lookin_3", 3, "Use a mirror to show baby both your face and theirs", 15, "Minimal everyday household items"),


    # ---- Not responding to sound ----
    ("Not responding to sound", "not_respon_1", 1, "Use soft rattles close to baby’s ear and wait for head turn", 5, "Minimal everyday household items"),
    ("Not responding to sound", "not_respon_2", 2, "Call baby’s name gently during daily routines", 10, "Minimal everyday household items"),
    ("Not responding to sound", "not_respon_3", 3, "Introduce musical toys with different tones", 15, "Minimal everyday household items"),

    # ---- No social smile ----
    ("No social smile", "no_social__1", 1, "Smile and exaggerate expressions during face-to-face play", 5, "Minimal everyday household items"),
    ("No social smile", "no_social__2", 2, "Gently tickle or use playful touch while smiling", 10, "Minimal everyday household items"),
    ("No social smile", "no_social__3", 3, "Play peek-a-boo to prompt smiling back", 15, "Minimal everyday household items"),

    # ---- No head holding ----
    ("No head holding", "no_head_ho_1", 1, "Activity idea for 'No head holding' at difficulty level 1 (to be reviewed by professional).", 5, "Minimal everyday household items"),
    ("No head holding", "no_head_ho_2", 2, "Activity idea for 'No head holding' at difficulty level 2 (to be reviewed by professional).", 10, "Minimal everyday household items"),
    ("No head holding", "no_head_ho_3", 3, "Activity idea for 'No head holding' at difficulty level 3 (to be reviewed by professional).", 15, "Minimal everyday household items"),

    # ---- Doesn’t play with hands ----
    ("Doesn’t play with hands", "doesn’t_pl_1", 1, "Activity idea for 'Doesn’t play with hands' at difficulty level 1 (to be reviewed by professional).", 5, "Minimal everyday household items"),
    ("Doesn’t play with hands", "doesn’t_pl_2", 2, "Activity idea for 'Doesn’t play with hands' at difficulty level 2 (to be reviewed by professional).", 10, "Minimal everyday household items"),
    ("Doesn’t play with hands", "doesn’t_pl_3", 3, "Activity idea for 'Doesn’t play with hands' at difficulty level 3 (to be reviewed by professional).", 15, "Minimal everyday household items"),

    # ---- Doesn’t follow object ----
    ("Doesn’t follow object", "doesn’t_fo_1", 1, "Activity idea for 'Doesn’t follow object' at difficulty level 1 (to be reviewed by professional).", 5, "Minimal everyday household items"),
    ("Doesn’t follow object", "doesn’t_fo_2", 2, "Activity idea for 'Doesn’t follow object' at difficulty level 2 (to be reviewed by professional).", 10, "Minimal everyday household items"),
    ("Doesn’t follow object", "doesn’t_fo_3", 3, "Activity idea for 'Doesn’t follow object' at difficulty level 3 (to be reviewed by professional).", 15, "Minimal everyday household items"),

    # ---- No eye contact ----
    ("No eye contact", "no_eye_con_1", 1, "Activity idea for 'No eye contact' at difficulty level 1 (to be reviewed by professional).", 5, "Minimal everyday household items"),
    ("No eye contact", "no_eye_con_2", 2, "Activity idea for 'No eye contact' at difficulty level 2 (to be reviewed by professional).", 10, "Minimal everyday household items"),
    ("No eye contact", "no_eye_con_3", 3, "Activity idea for 'No eye contact' at difficulty level 3 (to be reviewed by professional).", 15, "Minimal everyday household items"),

     # ---- Cannot roll over from back to tummy ----
    ("Cannot roll over from back to tummy", "cannot_rol_1", 1, "Activity idea for 'Cannot roll over from back to tummy' at difficulty level 1 (to be reviewed by professional).", 5, "Minimal everyday household items"),
    ("Cannot roll over from back to tummy", "cannot_rol_2", 2, "Activity idea for 'Cannot roll over from back to tummy' at difficulty level 2 (to be reviewed by professional).", 10, "Minimal everyday household items"),
    ("Cannot roll over from back to tummy", "cannot_rol_3", 3, "Activity idea for 'Cannot roll over from back to tummy' at difficulty level 3 (to be reviewed by professional).", 15, "Minimal everyday household items"),

    # ---- Not reaching out for object ----
    ("Not reaching out for object", "not_reachi_1", 1, "Activity idea for 'Not reaching out for object' at difficulty level 1 (to be reviewed by professional).", 5, "Minimal everyday household items"),
    ("Not reaching out for object", "not_reachi_2", 2, "Activity idea for 'Not reaching out for object' at difficulty level 2 (to be reviewed by professional).", 10, "Minimal everyday household items"),
    ("Not reaching out for object", "not_reachi_3", 3, "Activity idea for 'Not reaching out for object' at difficulty level 3 (to be reviewed by professional).", 15, "Minimal everyday household items"),

    # ---- Cannot sit without support ----
    ("Cannot sit without support", "cannot_sit_1", 1, "Activity idea for 'Cannot sit without support' at difficulty level 1 (to be reviewed by professional).", 5, "Minimal everyday household items"),
    ("Cannot sit without support", "cannot_sit_2", 2, "Activity idea for 'Cannot sit without support' at difficulty level 2 (to be reviewed by professional).", 10, "Minimal everyday household items"),
    ("Cannot sit without support", "cannot_sit_3", 3, "Activity idea for 'Cannot sit without support' at difficulty level 3 (to be reviewed by professional).", 15, "Minimal everyday household items"),

    # ---- Does not distinguish between known persons and strangers ----
    ("Does not distinguish between known persons and strangers", "does_not_d_1", 1, "Activity idea for 'Does not distinguish between known persons and strangers' at difficulty level 1 (to be reviewed by professional).", 5, "Minimal everyday household items"),
    ("Does not distinguish between known persons and strangers", "does_not_d_2", 2, "Activity idea for 'Does not distinguish between known persons and strangers' at difficulty level 2 (to be reviewed by professional).", 10, "Minimal everyday household items"),
    ("Does not distinguish between known persons and strangers", "does_not_d_3", 3, "Activity idea for 'Does not distinguish between known persons and strangers' at difficulty level 3 (to be reviewed by professional).", 15, "Minimal everyday household items"),

    # ---- Cannot sit up by himself ----
    ("Cannot sit up by himself", "cannot_situp_1", 1, "Activity idea for 'Cannot sit up by himself' at difficulty level 1 (to be reviewed by professional).", 5, "Minimal everyday household items"),
    ("Cannot sit up by himself", "cannot_situp_2", 2, "Activity idea for 'Cannot sit up by himself' at difficulty level 2 (to be reviewed by professional).", 10, "Minimal everyday household items"),
    ("Cannot sit up by himself", "cannot_situp_3", 3, "Activity idea for 'Cannot sit up by himself' at difficulty level 3 (to be reviewed by professional).", 15, "Minimal everyday household items"),

    # ---- Cannot stand without support ----
    ("Cannot stand without support", "cannot_sta_1", 1, "Encourage baby to pull up by holding onto sturdy furniture or your hands.", 5, "Minimal everyday household items"),
    ("Cannot stand without support", "cannot_sta_2", 2, "Use soft toys placed slightly above baby's reach to encourage standing effort.", 10, "Minimal everyday household items"),
    ("Cannot stand without support", "cannot_sta_3", 3, "Support baby in standing position for a few seconds, gradually reducing support.", 15, "Minimal everyday household items"),

    # ---- Immature grasp ----
    ("Immature grasp", "immature_g_1", 1, "Offer small soft toys that baby can easily hold and explore.", 5, "Minimal everyday household items"),
    ("Immature grasp", "immature_g_2", 2, "Encourage picking up small safe objects like cloth pieces or rings.", 10, "Minimal everyday household items"),
    ("Immature grasp", "immature_g_3", 3, "Play stacking games or pass toys between hands to improve coordination.", 15, "Minimal everyday household items"),

    # ---- Poor object manipulation and play ----
    ("Poor object manipulation and play", "poor_objec_1", 1, "Show baby how to shake or bang toys together.", 5, "Minimal everyday household items"),
    ("Poor object manipulation and play", "poor_objec_2", 2, "Encourage placing toys into a box and taking them out repeatedly.", 10, "Minimal everyday household items"),
    ("Poor object manipulation and play", "poor_objec_3", 3, "Introduce toys with different textures to explore handling and curiosity.", 15, "Minimal everyday household items"),

    # ---- No babbling ----
    ("No babbling", "no_babblin_1", 1, "Talk or sing to your baby face-to-face and pause for their response.", 5, "Minimal everyday household items"),
    ("No babbling", "no_babblin_2", 2, "Repeat baby’s cooing sounds and exaggerate mouth movements.", 10, "Minimal everyday household items"),
    ("No babbling", "no_babblin_3", 3, "Use toys that make sounds to encourage vocal imitation.", 15, "Minimal everyday household items"),

    # ---- No gestures ----
    ("No gestures", "no_gesture_1", 1, "Wave and clap frequently while speaking to your baby.", 5, "Minimal everyday household items"),
    ("No gestures", "no_gesture_2", 2, "Encourage pointing by asking baby to show or choose objects.", 10, "Minimal everyday household items"),
    ("No gestures", "no_gesture_3", 3, "Model common gestures like ‘bye-bye’, ‘come here’, or ‘give me’.", 15, "Minimal everyday household items"),

    # ---- Cannot walk ----
    ("Cannot walk", "cannot_wal_1", 1, "Hold baby’s hands and encourage short supported steps.", 5, "Minimal everyday household items"),
    ("Cannot walk", "cannot_wal_2", 2, "Place toys a few steps away to motivate baby to move forward.", 10, "Minimal everyday household items"),
    ("Cannot walk", "cannot_wal_3", 3, "Practice standing balance by holding baby’s hands lightly.", 15, "Minimal everyday household items"),

     # --- Little interest in surroundings and caregivers ---
    ("Little interest in surroundings and caregivers", "little_int_1", 1, "Activity for Little interest in surroundings and caregivers - Level 1", 5, "Minimal everyday household items"),
    ("Little interest in surroundings and caregivers", "little_int_2", 2, "Activity for Little interest in surroundings and caregivers - Level 2", 10, "Minimal everyday household items"),
    ("Little interest in surroundings and caregivers", "little_int_3", 3, "Activity for Little interest in surroundings and caregivers - Level 3", 15, "Minimal everyday household items"),

    # --- Absence or minimal eye-contact or smiling ---
    ("Absence or minimal eye-contact or smiling", "absence_or_1", 1, "Activity for Absence or minimal eye-contact or smiling - Level 1", 5, "Minimal everyday household items"),
    ("Absence or minimal eye-contact or smiling", "absence_or_2", 2, "Activity for Absence or minimal eye-contact or smiling - Level 2", 10, "Minimal everyday household items"),
    ("Absence or minimal eye-contact or smiling", "absence_or_3", 3, "Activity for Absence or minimal eye-contact or smiling - Level 3", 15, "Minimal everyday household items"),

    # --- Excessive clumsiness/ stumbling ---
    ("Excessive clumsiness/ stumbling", "excessive__1", 1, "Activity for Excessive clumsiness/ stumbling - Level 1", 5, "Minimal everyday household items"),
    ("Excessive clumsiness/ stumbling", "excessive__2", 2, "Activity for Excessive clumsiness/ stumbling - Level 2", 10, "Minimal everyday household items"),
    ("Excessive clumsiness/ stumbling", "excessive__3", 3, "Activity for Excessive clumsiness/ stumbling - Level 3", 15, "Minimal everyday household items"),

    # --- No '2-word' phrases ---
    ("No '2-word' phrases", "no_2word_1", 1, "Activity for No '2-word' phrases - Level 1", 5, "Minimal everyday household items"),
    ("No '2-word' phrases", "no_2word_2", 2, "Activity for No '2-word' phrases - Level 2", 10, "Minimal everyday household items"),
    ("No '2-word' phrases", "no_2word_3", 3, "Activity for No '2-word' phrases - Level 3", 15, "Minimal everyday household items"),

    # --- No meaningful play with toys ---
    ("No meaningful play with toys", "no_meaning_1", 1, "Activity for No meaningful play with toys - Level 1", 5, "Minimal everyday household items"),
    ("No meaningful play with toys", "no_meaning_2", 2, "Activity for No meaningful play with toys - Level 2", 10, "Minimal everyday household items"),
    ("No meaningful play with toys", "no_meaning_3", 3, "Activity for No meaningful play with toys - Level 3", 15, "Minimal everyday household items"),

    # --- Poor response to commands ---
    ("Poor response to commands", "poor_respo_1", 1, "Activity for Poor response to commands - Level 1", 5, "Minimal everyday household items"),
    ("Poor response to commands", "poor_respo_2", 2, "Activity for Poor response to commands - Level 2", 10, "Minimal everyday household items"),
    ("Poor response to commands", "poor_respo_3", 3, "Activity for Poor response to commands - Level 3", 15, "Minimal everyday household items"),

     # --- Prefers to play alone ---
    ("Prefers to play alone", "prefers_to_1", 1, "Activity for Prefers to play alone - Level 1", 5, "Minimal everyday household items"),
    ("Prefers to play alone", "prefers_to_2", 2, "Activity for Prefers to play alone - Level 2", 10, "Minimal everyday household items"),
    ("Prefers to play alone", "prefers_to_3", 3, "Activity for Prefers to play alone - Level 3", 15, "Minimal everyday household items"),

    # --- No imitation ---
    ("No imitation", "no_imitati_1", 1, "Activity for No imitation - Level 1", 5, "Minimal everyday household items"),
    ("No imitation", "no_imitati_2", 2, "Activity for No imitation - Level 2", 10, "Minimal everyday household items"),
    ("No imitation", "no_imitati_3", 3, "Activity for No imitation - Level 3", 15, "Minimal everyday household items"),

    # --- No pretend play ---
    ("No pretend play", "no_pretend_1", 1, "Activity for No pretend play - Level 1", 5, "Minimal everyday household items"),
    ("No pretend play", "no_pretend_2", 2, "Activity for No pretend play - Level 2", 10, "Minimal everyday household items"),
    ("No pretend play", "no_pretend_3", 3, "Activity for No pretend play - Level 3", 15, "Minimal everyday household items"),

    # --- Difficulty following simple instruction ---
    ("Difficulty following simple instruction", "difficulty_1", 1, "Activity for Difficulty following simple instruction - Level 1", 5, "Minimal everyday household items"),
    ("Difficulty following simple instruction", "difficulty_2", 2, "Activity for Difficulty following simple instruction - Level 2", 10, "Minimal everyday household items"),
    ("Difficulty following simple instruction", "difficulty_3", 3, "Activity for Difficulty following simple instruction - Level 3", 15, "Minimal everyday household items"),

    # --- Cannot dress by own self ---
    ("Cannot dress by own self", "cannot_dre_1", 1, "Activity for Cannot dress by own self - Level 1", 5, "Minimal everyday household items"),
    ("Cannot dress by own self", "cannot_dre_2", 2, "Activity for Cannot dress by own self - Level 2", 10, "Minimal everyday household items"),
    ("Cannot dress by own self", "cannot_dre_3", 3, "Activity for Cannot dress by own self - Level 3", 15, "Minimal everyday household items"),

    # --- Difficulty in learning new skills ---
    ("Difficulty in learning new skills", "difficulty_1", 1, "Activity for Difficulty in learning new skills - Level 1", 5, "Minimal everyday household items"),
    ("Difficulty in learning new skills", "difficulty_2", 2, "Activity for Difficulty in learning new skills - Level 2", 10, "Minimal everyday household items"),
    ("Difficulty in learning new skills", "difficulty_3", 3, "Activity for Difficulty in learning new skills - Level 3", 15, "Minimal everyday household items"),

    # --- Slow in daily activities ---
    ("Slow in daily activities", "slow_in_da_1", 1, "Activity for Slow in daily activities - Level 1", 5, "Minimal everyday household items"),
    ("Slow in daily activities", "slow_in_da_2", 2, "Activity for Slow in daily activities - Level 2", 10, "Minimal everyday household items"),
    ("Slow in daily activities", "slow_in_da_3", 3, "Activity for Slow in daily activities - Level 3", 15, "Minimal everyday household items"),

    # --- Poor recall ---
    ("Poor recall", "poor_recal_1", 1, "Activity for Poor recall - Level 1", 5, "Minimal everyday household items"),
    ("Poor recall", "poor_recal_2", 2, "Activity for Poor recall - Level 2", 10, "Minimal everyday household items"),
    ("Poor recall", "poor_recal_3", 3, "Activity for Poor recall - Level 3", 15, "Minimal everyday household items"),

    # --- Poor expressive language ---
    ("Poor expressive language", "poor_expre_1", 1, "Activity for Poor expressive language - Level 1", 5, "Minimal everyday household items"),
    ("Poor expressive language", "poor_expre_2", 2, "Activity for Poor expressive language - Level 2", 10, "Minimal everyday household items"),
    ("Poor expressive language", "poor_expre_3", 3, "Activity for Poor expressive language - Level 3", 15, "Minimal everyday household items"),

    # --- Behavioural problems ---
    ("Behavioural problems", "behavioura_1", 1, "Activity for Behavioural problems - Level 1", 5, "Minimal everyday household items"),
    ("Behavioural problems", "behavioura_2", 2, "Activity for Behavioural problems - Level 2", 10, "Minimal everyday household items"),
    ("Behavioural problems", "behavioura_3", 3, "Activity for Behavioural problems - Level 3", 15, "Minimal everyday household items"),
]



async def insert_activities():
    async with AsyncSessionLocal() as session:
        # ✅ Safely clear the table and reset the primary key
        await session.execute(text('TRUNCATE TABLE public.activities RESTART IDENTITY CASCADE;'))
        await session.commit()

        # ✅ Double-check table is empty
        count = await session.scalar(text('SELECT COUNT(*) FROM public.activities'))
        print("🔎 Activities count before insert:", count)

        objs = []
        for red_flag, activity_id, step, desc, minutes, materials in activities_data:
            objs.append(Activity(
                activity_id=activity_id,
                red_flag=red_flag,
                step_order=step,
                duration_days=10,
                duration_minutes=minutes,
                content_jsonb={
                    "description": desc,
                    "materials": materials,
                    "video_url": ""
                },
                alternatives=[],
                version="v1.0",
                created_by="system"
            ))

        session.add_all(objs)
        await session.commit()
        print(f"✅ Inserted {len(objs)} activities successfully!")

if __name__ == "__main__":
    asyncio.run(insert_activities())