/*  Copyright (c) MediaArea.net SARL. All Rights Reserved.
 *
 *  Use of this source code is governed by a GPLv3+/MPLv2+ license that can
 *  be found in the License.html file in the root of the source tree.
 */

#include <QWebPage>
#include <QWebFrame>
#include <QWebElement>
#include <QWebElementCollection>
#include <QFileDialog>

#include "mainwindow.h"
#include "WebPage.h"
#include <QtGlobal>

namespace MediaConch
{
    WebPage::WebPage(MainWindow *m, QWidget *parent) : QWebPage(parent), mainwindow(m)
    {
        connect(this, SIGNAL(loadFinished(bool)), this, SLOT(onLoadFinished(bool)));
    }

    void WebPage::onLoadFinished(bool ok)
    {
        if (!ok)
            return;

        QWebFrame* frame = mainFrame();
        frame->addToJavaScriptWindowObject("webpage", this);

        QWebElementCollection forms = frame->findAllElements("form");
        for (int i = 0; i < forms.count(); i++)
        {
            QWebElement form = forms[i];

            //Input with file to get the full file name
            QWebElementCollection inputs = form.findAll("input[type=\"file\"]");
            for (int j = 0; j < inputs.count(); j++)
            {
                QWebElement input = inputs[j];
                input.setAttribute("onclick", QString("webpage.onInputChanged(this.name);"));
            }

            //To know the check button pushed
            QWebElementCollection buttons = form.findAll("button[type=\"submit\"]");
            for (int j = 0; j < buttons.count(); j++)
            {
                QWebElement button = buttons[j];
                button.setAttribute("onclick", QString("webpage.onButtonClicked(this.id);"));
            }
        }

        QWebElementCollection uls = frame->findAllElements("ul");
        for (int i = 0; i < uls.count(); i++)
        {
            QWebElement form = uls[i];
            QWebElementCollection lis = form.findAll("li");
            for (int j = 0; j < lis.count(); j++)
            {
                QWebElement link = lis[j].findFirst("a");
                if (link.isNull())
                    break;
                link.setAttribute("onclick", QString("webpage.menu_link_checker(this.text);"));
            }
        }
    }

    void WebPage::menu_link_checker(const QString& name)
    {
        if (!name.compare("Checker"))
            mainwindow->checker_selected();
        else if (!name.compare("Policies"))
            mainwindow->policies_selected();
        else
            mainwindow->checker_selected();
    }

    void WebPage::onInputChanged(const QString& inputName)
    {
        select_file_name = inputName;
    }

    void WebPage::onButtonClicked(const QString& id)
    {
        button_clicked_id = id;
    }

    void WebPage::onFileUploadSelected(QWebElement form)
    {
        QWebElement policyElement = form.findFirst("#checkerUpload_step1_policy");
        QString policy = policyElement.evaluateJavaScript("this.value").toString();
        QString file = file_selector.value("checkerUpload[file]", QString());

        if (!file.length())
            return;
        mainwindow->checker_add_file(file, policy);
    }

    void WebPage::onFileOnlineSelected(QWebElement form)
    {
        QWebElement policyElement = form.findFirst("#checkerOnline_step1_policy");
        QString policy = policyElement.evaluateJavaScript("this.value").toString();
        QWebElement urlElement = form.findFirst("#checkerOnline_file");
        QString url = urlElement.evaluateJavaScript("this.value").toString();

        if (!url.length())
            return;
        mainwindow->checker_add_file(url, policy);
    }

    void WebPage::onFileRepositorySelected(QWebElement form)
    {
        QWebElement policyElement = form.findFirst("#checkerRepository_step1_policy");
        QString policy = policyElement.evaluateJavaScript("this.value").toString();
        QString dirname = file_selector.value("checkerRepository[directory]", QString());

        QDir dir(dirname);

        QFileInfoList list = dir.entryInfoList(QDir::Files);
        if (!list.count())
            return;
        mainwindow->checker_add_files(list, policy);
    }

    bool WebPage::acceptNavigationRequest(QWebFrame *frame, const QNetworkRequest& request,
                                          QWebPage::NavigationType type)
    {
        if (type == QWebPage::NavigationTypeFormSubmitted || type == QWebPage::NavigationTypeFormResubmitted)
        {
            QMapIterator<QString, QString> it(file_selector);
            QWebFrame *frame = currentFrame();
            QWebElement document = frame->documentElement();

            QWebElement button = document.findFirst(QString("button[id=\"%1\"]").arg(button_clicked_id));

            QString form_id = button.parent().parent().attribute("id");
            if (form_id == "checkerUpload")
                onFileUploadSelected(button.parent().parent());
            else if (form_id == "checkerOnline")
                onFileOnlineSelected(button.parent().parent());
            else if (form_id == "checkerRepository")
                onFileRepositorySelected(button.parent().parent());

            return false;
        }
        return QWebPage::acceptNavigationRequest(frame, request, type);
    }

    QString WebPage::chooseFile(QWebFrame *, const QString& suggested)
    {
        QString value_input;
        if (select_file_name == "checkerRepository[directory]")
            value_input = QFileDialog::getExistingDirectory(view(), NULL, suggested);
        else
            value_input = QFileDialog::getOpenFileName(view(), NULL, suggested);
        file_selector.insert(select_file_name, value_input);
        return value_input;
    }

    bool WebPage::extension(Extension extension, const ExtensionOption *option,
                            ExtensionReturn *output)
    {
        if (extension == QWebPage::ChooseMultipleFilesExtension)
        {
            QStringList suggested = ((const ChooseMultipleFilesExtensionOption*)option)->suggestedFileNames;
            QStringList names = QFileDialog::getOpenFileNames(view(), QString::null);
            ((ChooseMultipleFilesExtensionReturn*)output)->fileNames = names;
            return true;
        }
        return false;
    }

    bool WebPage::supportsExtension(Extension extension) const
    {
        if (extension == ChooseMultipleFilesExtension)
            return true;
        return false;
    }
    

}
