#include "boombox.h"

/*void Ui_Form::setupUi(QWidget *Form){
    if (Form->objectName().isEmpty()) Form->setObjectName("Form");
    Form->setEnabled(true);
    Form->resize(640, 480);
    QSizePolicy sizePolicy(QSizePolicy::Policy::Fixed, QSizePolicy::Policy::Fixed);
    sizePolicy.setHorizontalStretch(0);
    sizePolicy.setVerticalStretch(0);
    sizePolicy.setHeightForWidth(Form->sizePolicy().hasHeightForWidth());
    Form->setSizePolicy(sizePolicy);
    Form->setMinimumSize(QSize(640, 480));
    Form->setMaximumSize(QSize(640, 480));
    formWidget = new QWidget(Form);
    formWidget->setObjectName("formWidget");
    formWidget->setEnabled(true);
    formWidget->setGeometry(QRect(270, 200, 100, 80));
    verticalLayout = new QVBoxLayout(formWidget);
    verticalLayout->setObjectName("verticalLayout");
    verticalLayout->setSizeConstraint(QLayout::SizeConstraint::SetDefaultConstraint);
    verticalLayout->setContentsMargins(0, 0, 0, 0);
    pushButton_2 = new QPushButton(formWidget);
    pushButton_2->setObjectName("pushButton_2");
    pushButton_2->setLayoutDirection(Qt::LayoutDirection::LeftToRight);
    pushButton_2->setAutoFillBackground(false);

    verticalLayout->addWidget(pushButton_2);

    pushButton = new QPushButton(formWidget);
    pushButton->setObjectName("pushButton");

    verticalLayout->addWidget(pushButton);


    retranslateUi(Form);

    QMetaObject::connectSlotsByName(Form);
}

void Ui_Form::retranslateUi(QWidget *Form){
    Form->setWindowTitle(QCoreApplication::translate("Form", "Ritual", nullptr));
    pushButton_2->setText(QCoreApplication::translate("Form", "PushButton", nullptr));
    pushButton->setText(QCoreApplication::translate("Form", "PushButton", nullptr));
} // retranslateUi*/