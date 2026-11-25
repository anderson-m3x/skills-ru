/**
 * Start-routes: a row of task-shaped chips above the composer of a blank session.
 * Each chip writes the matching slash command into the draft, so the first
 * message of a session starts from a skill instead of from memory.
 */
window.__ModuleLoader__.load({
  id: '@local/start-routes',
  factory(require) {
    const React = require('react');
    const h = React.createElement;

    const NS = 'start-routes';

    /** Task-shaped entry points, in the order the row shows them. */
    const ROUTES = [
      { id: 'idea', skill: 'grill-with-docs' },
      { id: 'bug', skill: 'diagnosing-bugs' },
      { id: 'review', skill: 'code-review' },
      { id: 'research', skill: 'research' },
      { id: 'triage', skill: 'triage' },
      { id: 'prototype', skill: 'prototype' },
      { id: 'route', skill: 'ask-matt' },
    ];

    const ru = {
      'caption': 'Стартовые маршруты',
      'route.idea': 'Обсудить идею',
      'hint.idea': 'Грилл-интервью по идее; на выходе — GLOSSARY.md и ADR',
      'route.bug': 'Починить баг',
      'hint.bug': 'Диагностика: сначала петля обратной связи, потом фикс с регрессионным тестом',
      'route.review': 'Отревьюить код',
      'hint.review': 'Ревью диффа от фиксированной точки по осям Standards и Spec',
      'route.research': 'Исследовать вопрос',
      'hint.research': 'Фоновое исследование по первичным источникам, итог — markdown в репозитории',
      'route.triage': 'Триаж issue',
      'hint.triage': 'Разбор входящих issue и PR до состояния, готового для агента',
      'route.prototype': 'Прототип',
      'hint.prototype': 'Выбрасываемый код, который отвечает на один вопрос по дизайну',
      'route.route': 'Подобрать скилл',
      'hint.route': 'Спросить, с какого скилла начать, если задача неочевидная',
      'all': 'Все скиллы',
      'hint.all': 'Открыть полный список команд',
    };

    const en = {
      'caption': 'Starting routes',
      'route.idea': 'Discuss an idea',
      'hint.idea': 'Sharpening interview; ends with GLOSSARY.md and ADRs',
      'route.bug': 'Fix a bug',
      'hint.bug': 'Diagnosis: a feedback loop first, then a regression test',
      'route.review': 'Review the code',
      'hint.review': 'Diff review against a fixed point, on Standards and Spec',
      'route.research': 'Research a question',
      'hint.research': 'Background research from primary sources, written as markdown',
      'route.triage': 'Triage issues',
      'hint.triage': 'Turn incoming issues and PRs into agent-ready work',
      'route.prototype': 'Prototype',
      'hint.prototype': 'Throwaway code that answers one design question',
      'route.route': 'Pick a skill',
      'hint.route': 'Ask which skill to start with when the task is unclear',
      'all': 'All skills',
      'hint.all': 'Open the full command list',
    };

    // Theme tokens only: the row follows the active palette and never paints its own colors.
    const CSS = `
.dsh-start-routes{display:flex;flex-direction:column;align-items:center;gap:6px;padding:2px 12px 10px;box-sizing:border-box;}
.dsh-start-routes-caption{font-size:12px;line-height:1.4;color:var(--dsw-alias-label-tertiary);user-select:none;}
.dsh-start-routes-row{display:flex;flex-wrap:wrap;justify-content:center;gap:6px;}
.dsh-start-routes-chip{font-family:inherit;font-size:12px;line-height:1;padding:6px 10px;border-radius:999px;border:1px solid var(--dsw-alias-border-l1);background:var(--dsw-alias-bg-layer-1);color:var(--dsw-alias-label-secondary);cursor:pointer;white-space:nowrap;}
.dsh-start-routes-chip:hover{background:var(--dsw-alias-bg-layer-2);border-color:var(--dsw-alias-border-l2);color:var(--dsw-alias-label-primary);}
.dsh-start-routes-chip:focus-visible{outline:2px solid var(--dsw-focus-ring-color, var(--dsw-alias-state-business-primary));outline-offset:2px;}
.dsh-start-routes-chip[data-plain="true"]{border-style:dashed;}
`;

    /** Return the keyboard to the composer editor, best effort. */
    function focusComposer() {
      window.requestAnimationFrame(() => {
        const seat = document.querySelector('[data-composer-seat]');
        const editor = seat === null ? null : seat.querySelector('[contenteditable="true"]');
        if (editor !== null && typeof editor.focus === 'function') {
          editor.focus({ preventScroll: true });
        }
      });
    }

    function StartRoutes(props) {
      const { t, inputActions, useSession, useInput } = props;
      const blank = useSession(snapshot => snapshot.blank);
      const draft = useInput(state => state.draft);

      const pick = React.useCallback(token => {
        inputActions.setDraft(token);
        focusComposer();
      }, [inputActions]);

      if (blank !== true || draft.trim() !== '') return null;

      const chip = (key, label, hint, token, plain) => h('button', {
        key,
        type: 'button',
        className: 'dsh-start-routes-chip',
        title: t(hint),
        'data-plain': plain === true ? 'true' : undefined,
        onClick: () => { pick(token); },
      }, t(label));

      return h('div', { className: 'dsh-start-routes' }, [
        h('style', { key: 'style' }, CSS),
        h('div', { key: 'caption', className: 'dsh-start-routes-caption' }, t('caption')),
        h('div', {
          key: 'row',
          className: 'dsh-start-routes-row',
          role: 'group',
          'aria-label': t('caption'),
        }, [
          ...ROUTES.map(route => chip(route.id, `route.${route.id}`, `hint.${route.id}`, `/${route.skill} `)),
          chip('all', 'all', 'hint.all', '/', true),
        ]),
      ]);
    }

    return {
      inject: ['slots', 'locale'],
      apply(ctx) {
        ctx.effect(() => ctx.locale.register(NS, { ru, en }), 'start-routes: dictionaries');
        ctx.slots.inject('conversation.input.dock', () => ctx.slots.register({
          name: 'conversation.input.dock',
          id: 'start-routes',
          order: 20,
          locale: NS,
        }, StartRoutes));
      },
    };
  },
});
