// Allow anchor tags with role="button" to be triggered by the spacebar for accessibility.
document.querySelectorAll('a[role="button"]').forEach(button => {
    button.addEventListener('keydown', e => {
        // Prevent default browser action for spacebar (scrolling)
        if (e.code === 'Space') {
            e.preventDefault();
        }
    });
    button.addEventListener('keyup', e => {
        // Trigger click on spacebar release, mimicking native button behavior
        if (e.code === 'Space') {
            e.preventDefault();
            e.target.click();
        }
    });
});
