






// start wardriving
const startButton = document.getElementById('startWardriving');
startButton.addEventListener('click', startWardriving);
async function startWardriving() {
    const response = await fetch('/startWardriving');
    const data = await response.json();
    console.log(data);
}




