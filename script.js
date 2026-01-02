let CreateWorkoutButton = document.getElementById("CreateWorkout");

function show_create_workout_ui() {
    CreateWorkoutButton.textContent = 'GangGang';
}

CreateWorkoutButton.onclick = show_create_workout_ui;