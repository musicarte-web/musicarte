const btn = document.querySelector('.menu-btn');
const nav = document.querySelector('.main-nav');

if (btn && nav) {
    btn.addEventListener('click', () => {
        const open = nav.classList.toggle('open');

        btn.setAttribute('aria-expanded', String(open));
        btn.setAttribute(
            'aria-label',
            open ? 'Fechar menu' : 'Abrir menu'
        );
        btn.textContent = open ? '×' : '☰';
    });

    nav.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => {
            nav.classList.remove('open');
            btn.setAttribute('aria-expanded', 'false');
            btn.setAttribute('aria-label', 'Abrir menu');
            btn.textContent = '☰';
        });
    });
}