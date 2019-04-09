import bindAll from 'lodash.bindall';
import PropTypes from 'prop-types';
import React from 'react';
import {connect} from 'react-redux';
import storage from '../lib/storage';
import {projectTitleInitialState} from '../reducers/project-title';
import html2canvas from './html2canvas.min';



class UploadProduction extends React.Component {
    constructor (props) {
        super(props);
        bindAll(this, [
            'createProject',
            'updateProject',
            'SaveProject',
            'doStoreProject',
            'getPicture'
        ]);
    }
    SaveProject () {
        this.props.saveProjectSb3().then(content => {
            this.getPicture(this.props, content);
        });
    }

    getPicture (props, content){
        html2canvas(document.getElementsByClassName('stage_stage-wrapper_eRRuk box_box_2jjDp')[0])
            .then(canvas => {
                const image = new Image();
                image.src = canvas.toDataURL('image/png');
                const bytes = window.atob(image.src.split(',')[1]);
                // 处理异常,将ascii码小于0的转换为大于0
                const ab = new ArrayBuffer(bytes.length);
                const ia = new Uint8Array(ab);
                for (let i = 0; i < bytes.length; i++) {
                    ia[i] = bytes.charCodeAt(i);
                }
                const imgblob = new Blob([ab], {type: 'image/png'});
                // if (imgblob.size < 4300){
                if (false){
                    this.getPicture(props, content);
                } else {

                    function getCookie(cname)
                    {
                        let name = cname + "=";
                        let ca = document.cookie.split(';');
                        for(let i=0; i<ca.length; i++)
                        {
                            let c = ca[i].trim();
                            if (c.indexOf(name)===0) return c.substring(name.length,c.length);
                        }
                        return "";
                    }
                    let username = getCookie('username');
                    if(username === ''){
                        alert("请先登录！");
                    }else{
                        const form = new FormData();
                        form.append('image', imgblob, 'image.png');
                        form.append('file', content);
                        form.append('author', username);
                        form.append('name', props.projectFilename.toString().slice(0, -4));
                        if(window.productionID !== null){
                            form.append('uploadType', 'update');
                            form.append('productionID', window.productionID);
                        }else{
                            form.append('uploadType', 'create');
                            form.append('createType', window.createProductionType);
                        }

                        const xmlhttp = new XMLHttpRequest();
                        xmlhttp.onreadystatechange = function stateChange (){
                            if (xmlhttp.readyState === 4){
                                let response = eval("(" + xmlhttp.responseText + ")");
                                alert(response.mess);
                            }
                        };
                        const url = 'http://' + window.location.host.toString() + '/team_match/upload_production/';
                        xmlhttp.open('POST', url, true);
                        xmlhttp.send(form);
                    }
                }
            });
    }

    doStoreProject (id) {
        return this.props.saveProjectSb3()
            .then(content => {
                const assetType = storage.AssetType.Project;
                const dataFormat = storage.DataFormat.SB3;
                const body = new FormData();
                body.append('sb3_file', content, 'sb3_file');
                return storage.store(
                    assetType,
                    dataFormat,
                    body,
                    id
                );
            });
    }
    createProject () {
        return this.doStoreProject();
    }
    updateProject () {
        return this.doStoreProject(this.props.projectId);
    }
    render () {
        const {
            children
        } = this.props;
        return children(
            this.SaveProject,
            this.updateProject,
            this.createProject
        );
    }
}

const getProjectFilename = (curTitle, defaultTitle) => {
    let filenameTitle = curTitle;
    if (!filenameTitle || filenameTitle.length === 0) {
        filenameTitle = defaultTitle;
    }
    return `${filenameTitle.substring(0, 100)}.sb3`;
};

UploadProduction.propTypes = {
    children: PropTypes.func,
    projectFilename: PropTypes.string,
    projectId: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    saveProjectSb3: PropTypes.func
};

const mapStateToProps = state => ({
    saveProjectSb3: state.scratchGui.vm.saveProjectSb3.bind(state.scratchGui.vm),
    projectFilename: getProjectFilename(state.scratchGui.projectTitle, projectTitleInitialState),
    projectId: state.scratchGui.projectId
});

export default connect(
    mapStateToProps,
    () => ({}) // omit dispatch prop
)(UploadProduction);
