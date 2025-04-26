function randomInt(max) {
    return Math.floor(Math.random() * (max * 2 + 1));
}

function roll_check() {
    let res1 = randomInt(
        document.getElementById("aspect_dice_points").valueAsNumber
    );
    let res2 = randomInt(
        document.getElementById("aspect_dice_points").valueAsNumber
    );
    document.getElementById("aspect_result").value = res1;
    document.getElementById("aspect_result_risk").value = res2;
    let risky = document.getElementById("aspect_risky").checked;
    let savety = document.getElementById("aspect_savety").valueAsNumber;
    if (risky) {
        if (res2 > res1 + savety) {
            document.getElementById("aspect_value").style.background = "#ff6666";
            document.getElementById("aspect_rest").style.background = "#ff6666";
        } else {
            document.getElementById("aspect_value").style.background = "#99ff99";
            document.getElementById("aspect_rest").style.background = "#99ff99";
        }
    } else {
        document.getElementById("aspect_value").style.background = "#f1f1f1";
        document.getElementById("aspect_rest").style.background = "#f1f1f1";
    }
    calc_aspect_value();
}

function calc_aspect_value() {
    let ap = document.getElementById("aspect_result").valueAsNumber;
    let cost = 1;
    let resistance = document.getElementById("aspect_resistance").valueAsNumber;
    let duration = ""
    let savety = document.getElementById("aspect_savety").valueAsNumber;
    if (document.getElementById("aspect_single_use").checked) {
        cost = cost * 1;
        duration = "";
    }
    if (document.getElementById("aspect_scene").checked) {
        cost = cost * 2;
        duration = " s";
    }
    if (document.getElementById("aspect_mission").checked) {
        cost = cost * 4;
        duration = " m";
    }
    if (document.getElementById("aspect_campaign").checked) {
        cost = cost * 8;
        duration = " c";
    }
    if (document.getElementById("aspect_multi_target").checked) {
        cost = cost * 2;
    }
    let val = Math.floor(Math.max(ap - savety, 0) / cost) - resistance;
    let rest = Math.floor(Math.max(ap - savety, 0) % cost);
    if (resistance > 0) {
        document.getElementById("aspect_value").value = val + "[" + resistance + "]" + duration;
    } else {
        document.getElementById("aspect_value").value = val + duration;
    }
    document.getElementById("aspect_rest").value = rest;
    if (document.getElementById("aspect_risky").checked) {
        document.getElementById("aspect_savety").hidden = false;
    } else {
        document.getElementById("aspect_savety").hidden = true;
    }
    return
}
