import React, { useState } from 'react';

const AccordionSection = ({ title, children, defaultOpen = true, sectionNumber }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <section className="conf-step">
      <header
        className={`conf-step__header ${isOpen ? 'conf-step__header_opened' : 'conf-step__header_closed'}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <h2 className="conf-step__title">
          {sectionNumber && <span className="conf-step__number">{sectionNumber}</span>}
          {title}
        </h2>
      </header>
      {isOpen && <div className="conf-step__wrapper">{children}</div>}
    </section>
  );
};

export default AccordionSection;