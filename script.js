let Buttons = document.getElementsByClassName("Button");

function show_create_workout_ui() {
    let CreateWorkoutButton = document.getElementById("CreateWorkout");
    CreateWorkoutButton.textContent = 'GangGang';
}

function align_all_ui_formatting() {
    let Workouts = document.getElementsByClassName("Workout");
    let offset = 0;
    for (let i = 0; i < Workouts.length; i++) {
        align_ui_formatting(Workouts[i]);
        Workouts[i].style.top = offset + 20 + "px";
        offset += Workouts[i].offsetHeight + 20;
    }
}

function align_ui_formatting(Workout) {
    let children = Workout.children;
    let offset = 0;
    for (let i = 0; i < children.length; i++) {
        children[i].style.top = offset + "px";
        offset += children[i].offsetHeight;
    }
}

function setup_buttons(buttons) {
    for (let i = 0; i < buttons.length; i++) {
        buttons[i].onclick = window[buttons[i].getAttribute("function")];
    }
}

align_all_ui_formatting();
setup_buttons(Buttons);